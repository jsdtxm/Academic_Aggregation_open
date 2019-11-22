from __future__ import absolute_import, unicode_literals

import os,time,json,re
from mainapp.models import *
from celery import shared_task
from urllib.parse import parse_qs, unquote,urlparse,parse_qsl
from requests_html import HTML, HTMLSession
from Academic_Aggregation import celery_app as app
import random
from django.core.cache import cache
from .likelihood import likelihood
import langid

redis_on = True

def bd_access_token():
    
    cache_access_token = cache.get('access_token')
    if cache_access_token:
        # print('已缓存')
        return cache_access_token
    
    access_token_url = 'https://aip.baidubce.com/oauth/2.0/token'
    session = HTMLSession()

    access_token_request = session.post(
        access_token_url,
        data={
        'grant_type': 'client_credentials',
        'client_id': '',
        'client_secret':'',
        },
        headers={'Content-Type': 'application/json'}
    ).json()
    
    expires_in = access_token_request.get('expires_in')

    access_token = access_token_request.get('access_token')
    cache.set('access_token', access_token, expires_in-30)
    # print(access_token)
    return access_token

def lang_detection(ustr):
    '语种识别'
    lineTuple = langid.classify(ustr)
    return lineTuple[0]

def find_same(title,abstract):
    """判断是否有相同文献"""
    liters = Literature.objects.filter(title=title)

    access_token = bd_access_token()
    
    max_id = -1
    max_sim = 0
    for liter in liters:
        # print(liter)
        if not liter.abstract:
            continue

        sim = likelihood(abstract,liter.abstract)
        # print(sim)
        if sim > max_sim and sim > 0.8 :
            max_sim = sim
            max_id = liter.id
    
    return max_id

def weight_calc(cited,sore_year):
    '''权重计算'''
    try:
        cited = int(cited)
    except:
        cited = 0

    try:
        sore_year = int(sore_year)
    except:
        sore_year = 0

    #权重处理
    year_count = (sore_year - 1665) / (2019 - 1665)
    cited_count = cited / 200

    weight = year_count + cited_count*2

    return weight

def kword_comp(keywords):
    kes = ""
    for item in keywords:
        kes += '+'+item
    return kes[1:]

def gen_cited_text(liter):
    '''备份的获取引用连接，需求标题、作者、发表、年代'''
    try:
        cited_text = ""
        authors = json.loads(liter.authors)
        for author in authors[:-1]:
            cited_text += author + ', '
        cited_text += authors[-1] + '. '
        cited_text += liter.title + '[J]. '
        try:
            cited_text += liter.publish + ', '
        except:
            pass
        cited_text += str(liter.sore_year)

        liter.sc_quote = json.dumps({"sc_GBT7714":cited_text})
        
    except:
        liter.sc_quote = json.dumps({"sc_GBT7714":"ERROR"})
    
    liter.save()
    return cited_text

@app.task(bind=True)
def bd_get_cited(self,url):
    '''获取引用连接'''
    liter = Literature.objects.get(source_url=url)
    if liter.sc_quote:
        #若已经处理过
        return False
    
    session = HTMLSession()
    cited_url = "http://xueshu.baidu.com/u/citation?&sign=aa&url=" + liter.source_url + "&t=cite"
    r = session.get(cited_url).html
    res_json = json.loads(r.html)
    print(res_json)
    if not ( 'sc_GBT7714' in res_json ) or res_json['sc_GBT7714'] == False:
        gen_cited_text(liter)
        return False
    res_json.pop('request')
    res_json.pop('errno')
    liter.sc_quote = json.dumps(res_json)
    liter.save()

@app.task(bind=True)
def bd_get_quotes(self,paperid):
    '''获取参考文献'''

    source_liter = Literature.objects.get(paperid=paperid)
    if source_liter.sc_quote :
        #若已经处理过
        return False
    
    try:    
        url = 'http://xueshu.baidu.com/usercenter/paper/search?wd=citepaperuri:('+ paperid + ')&type=reference&rn=20&page_no='
        session = HTMLSession()
        r = session.get(url+ '1').json()

        num = r['data']['total_page_num']
        quotes = []
        for i in range(1,num):
            if i > 1:
                r = session.get(url+ str(i)).json()
            for paper in r['data']['papers']:
                paperid = paper['meta_di_info']['sc_longsign'][0]

                liter = Literature.objects.filter(paperid=paperid)
                if len(liter) > 0:
                    liter = liter[0]
                else:
                    liter = Literature()
                    liter.paperid = paperid
                try:
                    liter.source_url = paper['meta_di_info']['sc_scholarurl'][0]
                except:
                    pass
                try:
                    liter.doi = paper['meta_di_info']['sc_doi'][0].replace('',"")
                except:
                    pass
                
                liter.sore_year = paper['meta_di_info']['sc_year'][0]
                liter.abstract = paper['meta_di_info']['sc_abstract'][0]
                liter.all_version = json.dumps(paper['meta_di_info']['sc_all_version_url'][0])
                authors = []
                for author in paper['meta_di_info']['sc_author']:
                    authors.append(author['sc_name'][1])
                liter.authors = json.dumps(authors)
                liter.cited = paper['meta_di_info']['sc_cited'][0]
                try:
                    liter.keywords = json.dumps(paper['meta_di_info']['sc_keyword'][0])
                except:
                    pass

                if paper['meta_di_info'].get('sc_publish')!= None :
                    publish = paper['meta_di_info']['sc_publish'][0]
                    if publish.get('sc_journal') != None :
                        liter.publish = publish['sc_journal'][0]
                        liter.ltype = 0
                    elif publish.get('sc_conference') != None :
                        liter.publish = publish['sc_conference'][0]
                        liter.ltype = 3
                    elif publish.get('sc_booktitle') != None :
                        liter.publish = publish['sc_booktitle'][0]
                        liter.ltype = 2
                    elif publish.get('sc_publisher') != None :
                        liter.publish = publish['sc_publisher'][0]

                liter.title = paper['meta_di_info']['sc_title'][0]
                liter.collect_from = "百度学术"

                #TODO 这部分先屏蔽了再说，防止爆数据库
                # liter.save()
                quotes.append(gen_cited_text(liter))

        source_liter.quotes = json.dumps(quotes)
        source_liter.save()

    except Exception as exc:
        raise self.retry(countdown=60, max_retries=3, exc=exc)
    
    return True

@app.task(bind=True)
def bd_paper(self,paperid):

    try:
        liter = Literature.objects.filter(paperid=paperid)[0]
        new = False
        # if liter.detailed:
        #     #若已经处理过
        #     return False
    except:
        liter = Literature(
            paperid = paperid,
        )
        new = True
    
    try:
        session = HTMLSession()

        url = "http://xueshu.baidu.com/usercenter/paper/show?paperid="+paperid
        r = session.get(url).html

        main_info = r.find('.main-info',first=True)

        try:
            dtl_r_item = r.find('.dtl_r_item',first=True).find('h3',first=True)[2:]
            if dtl_r_item == '期刊':
                liter.ltype = 0
            elif dtl_r_item == '会议':
                liter.ltype = 3
        except:
            pass

        title_ele = main_info.find('h3 a',first=True)
        title = title_ele.text
        
        doi_ele = main_info.find('.doi_wr .kw_main',first=True)
        doi = doi_ele.text if doi_ele else ""

        authors = []
        for author in main_info.find('.author_wr .author_text span a'):
            authors.append(author.text)

        keywords = []
        for keys in main_info.find('.kw_wr .kw_main')[0].find('span'):
            keywords.append(keys.text)

        if len(keywords) <= 1:
            #处理百度出错的一种情况
            keywords = keywords[0].split(' ')
        
        allversion_content = r.find('.allversion_content',first=True)
        all_version = {}
        v_item_span = allversion_content.find('.dl_item_span')
        for vi in v_item_span:
            if vi.text == '查看更多':
                continue
            all_version[vi.text] = vi.find('.dl_item',first=True).attrs['href']

        liter.doi = doi
        if not liter.title or len(liter.title) < len(title):
            liter.title = title

        liter.authors = json.dumps(authors)
        try:
            liter.abstract = main_info.find('.abstract_wr .abstract',first=True).text
        except:
            liter.abstract = ""
        liter.keywords = json.dumps(keywords)
        liter.all_version = json.dumps(all_version)

        if new:
            liter.source_url = title_ele.absolute_links.pop()
            liter.cited = main_info.find('.ref_wr .ref-wr-num',first=True).text
            liter.publish = r.find('.journal_title',first=True).text
            liter.sore_year = r.find('.journal_content',first=True).text.split('年')[0]
        
        liter.detailed = True
        liter.save()
    except Exception as exc:
        raise self.retry(countdown=60, max_retries=3, exc=exc)

    return True

@app.task(bind=True)
def bd_search_orm(self,keywords,page):
    session = HTMLSession()
    pattern = re.compile(r'[(](.*)[)]', re.S)

    url = 'http://xueshu.baidu.com/s?wd=' + kword_comp(keywords) + '&pn=' + str(page*10)
    r = session.get(url).html
    list_items = r.find('.sc_default_result')

    result_list = []
    for item in list_items:
        try:
            c_font = item.find('.c_font',first=True)

            ltype = 0
            if len(c_font.find(".c-icon")) > 0:
                try:
                    ltype_text = c_font.find(".c-icon",first=True).attrs.get('class')[-1].split('-')[2]
                except:
                    pass
                if ltype_text == 'tushu':
                    ltype = 2
                elif ltype_text == 'zhuanli':
                    ltype = 4
                
            detail_url = unquote(c_font.absolute_links.pop()).replace(':(','=').replace(')','').replace('wd=','&')

            paperid = parse_qs(detail_url)['paperuri'][0]

            #进行一次查重,重复就跳过
            sim_liter = Literature.objects.filter(paperid=paperid)
            if len(sim_liter) > 0:
                result_list.append(sim_liter[0])
                continue

            authors = []
            sc_info = item.find('.sc_info',first=True).find('span')
            for au in sc_info[0].find('a'):
                authors.append(au.text)
            
            publish = None
            cited = None
            for info in sc_info[1:]:
                # print(info.html)
                sc_data_elem = info.find('a',first=True)
                if not sc_data_elem:
                    continue
                sc_data = sc_data_elem.attrs.get('data-click')
                if sc_data == "{'button_tp':'publish'}":
                    publish = sc_data_elem.text.replace('《',"").replace('》',"")
                elif sc_data == "{'button_tp':'sc_cited'}":
                    cited = sc_data_elem.text
            
            sore_year = info.find(".sc_time",first=True).text[:-1]
            
            all_version = {}
            v_item_span = item.find('.v_item_span')
            for vi in v_item_span:
                all_version[vi.text] = re.sub(pattern,"", vi.absolute_links.pop())

            title = item.find('.c_font',first=True).text
            abstract = item.find('.c_abstract',first=True).text.replace('摘　要:',"").replace("...","").strip()
            source_url = item.attrs['mu'].strip()
            
            liter = Literature(
                language = 0 if lang_detection(abstract[:20]) == 'zh' else 1,
                ltype = ltype,
                title = title,
                authors = json.dumps(authors),
                publish = publish,
                sore_year = sore_year if type(sore_year) == type(123) else None,
                cited = cited if type(cited) == type(123) else None,
                abstract = abstract,
                paperid = paperid,
                source_url = source_url,
                all_version = json.dumps(all_version),
                collect_from = "百度学术",
                weight = weight_calc(cited,sore_year),
            )
            
            liter.save()
            result_list.append(liter)

            if redis_on :
                bd_paper.apply_async(args=(paperid,), countdown=random.randint(1,10),  queue='low_priority')
                bd_get_cited.apply_async(args=(source_url,), countdown=random.randint(1,10),  queue='low_priority')
                bd_get_quotes.apply_async(args=(paperid,), countdown=random.randint(1,10),  queue='low_priority')
                 
        except Exception as exc:
            print(exc)
            raise self.retry(countdown=60, max_retries=3, exc=exc)
    return result_list

@app.task(bind=True)
def cnki_get_quotes(self,liter_id):
    '''获取参考文献'''
    liter = Literature.objects.get(pk=liter_id)
    if liter.quotes:
        return False

    try:
        result_query = json.loads(liter.cnki_info)
        session = HTMLSession()
        url = "http://kns.cnki.net/kcms/detail/frame/list.aspx?dbcode="+result_query['dbcode']+"&filename="+result_query['filename']+"&dbname="+result_query['dbname']+"&RefType=1&vl="
        r = session.get(url).html

        quotes = []
        for easybox in r.find('.essayBox'):
            for quote in easybox.find('li'):
                count = quote.find('em',first=True).text
                quotes.append(quote.text[len(count):].replace('\xa0\xa0',""))
        
        # print(quotes)
        liter.quotes = json.dumps(quotes)
        liter.save()
    except Exception as exc:
        raise self.retry(countdown=60, max_retries=3, exc=exc)
    
    return True

@app.task(bind=True)
def cnki_paper(self,url):
    try:
        liter = Literature.objects.filter(source_url=url)[0]
        new = False

        # print(liter.id)
        if liter.detailed:
            #若已经处理过
            return False
    except:
        liter = Literature(source_url = url,)
        new = True

    try:
        session = HTMLSession()

        r = session.get(url).html
        list_items = r.find('.sc_default_result')

        wxmain = r.find('.wxmain',first=True)
        liter.title = wxmain.find('h2.title',first=True).text

        authors = []
        for author in wxmain.find('.author a'):
            authors.append(author.text)
        liter.authors = json.dumps(authors)

        orgns = []
        for orgn in wxmain.find('.orgn a'):
            orgns.append(orgn.text)
        liter.institution = json.dumps(orgns)

        liter.abstract = wxmain.find('#ChDivSummary',first=True).text

        key_words = []
        try:
            for key_word in wxmain.xpath('.//label[@id="catalog_KEYWORD"]/..')[0].find('a'):
                key_words.append(key_word.text.replace(';','').replace('；',""))
            liter.keywords = json.dumps(key_words)
        except:
            pass

        try:
            liter.doi = json.dumps(wxmain.xpath('.//label[@id="catalog_ZCDOI"]/..')[0].text.replace("DOI：",""))
        except:
            pass
        
        download_links = {}
        for link in wxmain.find("#DownLoadParts",first=True).find('a'):
            download_links[link.text] = 'http://kns.cnki.net' + link.attrs['href'].strip()
        liter.savelink = json.dumps(download_links)

        try:
            liter.page = wxmain.find(".total",first=True).find('b')[1].text
        except:
            pass
        
        liter.detailed = True
        liter.collect_from = "中国知网"
        gen_cited_text(liter)
        liter.save()
    except Exception as exc:
        raise self.retry(countdown=60, max_retries=3, exc=exc)

    return True

@app.task(bind=True)
def cnki_search(self,keywords,page):
    session = HTMLSession()

    result_url = "http://kns.cnki.net/KCMS/detail/detail.aspx?"
    url = 'http://search.cnki.net/search.aspx?q='+str(keywords)+'&rank=citeNumber&cluster=all&val=CJFDTOTAL&p='+ str(page)
    r = session.get(url).html

    list_items = r.find('.wz_content')
    result_list = []
    
    for item in list_items:
        try:
            title = item.find('h3')[0].text.replace(" class='red_title'>","").replace("class='red_title'>","").replace("《","").replace("》","")
            abstract = item.find('.width715')[0].text

            #查重
            sim_liter_id = find_same(title,abstract)
            if sim_liter_id != -1:
                result_list.append(Literature.objects.get(pk=sim_liter_id))
                continue

            sim_liter = Literature.objects.filter(title = title)
            if len(sim_liter) > 0:
                result_list.append(sim_liter[0])
                continue

            result_query = {}
            for link in item.absolute_links:
                url_query = dict((x, y) for x, y in parse_qsl(urlparse(link).query))
                if link.find('epub.cnki.net') != -1:
                    result_query['dbname'] = url_query['dbname']
                    result_query['filename'] = url_query['filename']
                if link.find('search.cnki.net') != -1:
                    result_query['dbcode'] = url_query['dbcode']

            source_url = result_url + 'dbname=' +result_query['dbname'] + '&' + 'filename=' + result_query['filename']
            # print(source_url)
            sp = item.find('.year-count')[0].find('span')
            publish = sp[1].attrs['title']
            
            year_pos = sp[1].text.find("年")

            sore_year = sp[1].text[year_pos-4:year_pos]
            cnki_info = json.dumps(result_query)

            cited = sp[2].text.split('（')[-1][:-1]

            liter = Literature(
                language = 0 if lang_detection(abstract[:20]) == 'zh' else 1,
                title = title,
                publish = publish,
                sore_year = sore_year if type(sore_year) == type(123) else None,
                cited = cited if type(cited) == type(123) else None,
                abstract = abstract,
                source_url = source_url,
                cnki_info = cnki_info,
                collect_from = "中国知网",
                weight = weight_calc(cited,sore_year),
            )
            liter.save()
            result_list.append(liter)

            cnki_get_quotes.apply_async(args=(liter.id,), countdown=random.randint(1,10),  queue='low_priority')
            cnki_paper.apply_async(args=(source_url,), countdown=random.randint(1,10),  queue='low_priority')

        except Exception as exc:
            print(exc)
            raise self.retry(countdown=60, max_retries=3, exc=exc)
    return result_list
