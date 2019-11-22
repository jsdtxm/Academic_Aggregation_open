from multiprocessing import Process

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.contrib import auth

from requests_html import HTML, HTMLSession

from mainapp.models import *
import random
from .auth_form import *
from django.core.cache import cache
from .tasks import *

def weight_orm(elem):
    return elem.weight

def index(request):
    user = request.user.myuser if request.user.is_authenticated else None

    status = request.GET.get('status', '')

    content = {
        'active_menu': 'index',
        'user': user,
        'status':status,
    }

    if request.method == 'POST':
        return source_list(request)
                
    return render(request, 'backstage/index.html', content)

def test(request):
    user = request.user.myuser if request.user.is_authenticated else None

    # print(testfunc.apply_async((2, 2), queue='high_priority', countdown=10))

    # bd_search_orm(['爬虫','搜索'],0)
    # bd_search_orm.apply_async((['爬虫','搜索'],0),  queue='high_priority')
    bd_paper('5c3796066252ba7af3b9907611e4f9d2')
    # bd_paper.apply_async(args=('1e124b5ac160fd29a4a70d6af1ac6ee0',), countdown=random.randint(1,10),  queue='low_priority')

    # find_same("有压供水管道中气囊运动的危害与防护","分析了有压管道内气体的产生条件、运动特点以及气爆型水锤产生的机理 ,并就相应的防护措施进行了简要分析")
    # cnki_paper('http://kns.cnki.net/KCMS/detail/detail.aspx?dbname=CJFD2005&filename=JSJY200509000')
    # cnki_search(['爬虫','搜索'],0)
    # gen_cited_text(Literature.objects.get(pk=1306))
    # bd_get_quotes('1e124b5ac160fd29a4a70d6af1ac6ee0')
    content = {
        'active_menu': 'index',
        'user': user,
    }
    return render(request, 'backstage/index.html', content)

def test2(request):
    user = request.user.myuser if request.user.is_authenticated else None

    content = {
        'active_menu': 'index',
        'user': user,
    }
    return render(request, 'backstage/index.html', content)

def profile(request):
    return index(request)
    # user = request.user.myuser if request.user.is_authenticated else None
    # content = {
    #     'active_menu': 'profile',
    #     'user': user,
    # }
    # return render(request, 'backstage/profile.html', content)

def detail(request):
    user = request.user.myuser if request.user.is_authenticated else None
    
    paper_id = request.GET.get('id')
    try:
        literature = Literature.objects.get(pk=paper_id)
    except:
        return HttpResponse(status=404)
    
    if request.method == 'POST':# 获取对象
        obj = request.FILES.get('pdf')

        literature.upfile = obj
        literature.save()
    
    # else:
    #     if not literature.ai_keyword and literature.title and literature.abstract:
    #         try:
    #             url = "https://aip.baidubce.com/rpc/2.0/nlp/v1/keyword"
    #             session = HTMLSession()
    #             access_token = bd_access_token()

    #             if access_token:
    #                 keyword_request = session.post(
    #                     url+'?access_token='+access_token,
    #                     json={
    #                         'title': literature.title[:80],
    #                         'content': literature.abstract,
    #                     },
    #                     headers={'Content-Type': 'application/json','charset':'utf-8'}
    #                 )
    #                 keyword_request.encoding = 'gbk'
    #                 keyword_request_json = keyword_request.json()

    #                 key_items = keyword_request_json.get('items')
    #                 if key_items:
    #                     ai_kws = []
    #                     for ki in key_items:
    #                         ai_kws.append(ki['tag'])
    #                     # print(ai_kws)
    #                     literature.ai_keyword = json.dumps(ai_kws)
    #                     literature.save()
    #         except Exception as e:
    #             print(e)

    try:
        uni_list = json.loads(literature.quotes)
    except:
        uni_list = []
    try:
        all_version = json.loads(literature.all_version)
    except:
        all_version = {}
    
    try:
        keywords = json.loads(literature.keywords)
    except:
        keywords = None
    try:
        ai_keyword = json.loads(literature.ai_keyword)
    except:
        ai_keyword = None
    try:
        savelink = json.loads(literature.savelink)
    except:
        savelink = None

    content = {
        'active_menu': 'detail',
        'user': user,
        'literature':literature,
        'uni_list':uni_list,
        'all_version':all_version,
        'keywords':keywords,
        'ai_keyword':ai_keyword,
        'savelink':savelink,
    }
    return render(request, 'backstage/detail.html', content)

def pdf_view(request):
    user = request.user.myuser if request.user.is_authenticated else None
    
    paper_id = request.GET.get('id')
    try:
        literature = Literature.objects.get(pk=paper_id)
    except:
        return HttpResponse(status=404)
    
    content = {
        'active_menu': 'detail',
        'user': user,
        'literature':literature,
    }
    return render(request, 'backstage/pdf_view.html', content)


@login_required
def source_list(request):
    user = request.user.myuser if request.user.is_authenticated else None

    content = {
        'active_menu': 'source_list',
        'user': user,
    }

    if request.method == 'POST':
        key_words = request.POST.get('search')
        key_words = key_words.replace(','," ").replace('，'," ").split(" ")

        result_bd = bd_search_orm(key_words,0)
        result_cnki = cnki_search(key_words,0)

        result_list = result_bd + result_cnki
        result_list = list(set(result_list))
        result_list.sort(key=weight_orm,reverse = True)

        paginator = Paginator(result_list, 10)
        page = request.GET.get('page')
        
        # try:
        #     contacts = paginator.page(page)
        # except PageNotAnInteger:
        #     contacts = paginator.page(1)
        # except EmptyPage:
        #     contacts = paginator.page(paginator.num_pages)

        print(result_list)

        content['uni_list'] = result_list
        # content['uni_list'] = contacts
        content['key_words'] = key_words
        # content['page_range'] = paginator.page_range[contacts.number-1:contacts.number+5]
        # content['number'] = contacts.number

        # print(result_list[0].title)
        return render(request, 'backstage/source_list.html', content)

    return render(request, 'backstage/source_list.html', content)

@login_required
def favourite_list(request):
    user = request.user.myuser if request.user.is_authenticated else None

    favourites = Favorites.objects.filter(user=user.user).order_by('-upload_date')
    uni_list = []
    for item in favourites:
        uni_list.append(item.literature)
    paginator = Paginator(uni_list, 10)
    page = request.GET.get('page')
    key_words = ['爬虫','搜索']
    
    try:
        contacts = paginator.page(page)
    except PageNotAnInteger:
        contacts = paginator.page(1)
    except EmptyPage:
        contacts = paginator.page(paginator.num_pages)

    content = {
        'active_menu': 'favourite_list',
        'user': user,
        'uni_list':contacts,
        'key_words':key_words,
        'page_range':paginator.page_range[contacts.number-1:contacts.number+5],
        'number':contacts.number,
    }
    return render(request, 'backstage/favourite_list.html', content)

@login_required
def favourite_paper(request):
    user = request.user.myuser if request.user.is_authenticated else None

    paper_id = request.GET.get('id')
    try:
        paper = Literature.objects.get(pk=paper_id)
    except:
        return JsonResponse({"status":"error"})

    favourite = Favorites.objects.filter(user=user.user,literature=paper)
    if len(favourite) > 0:
        #已收藏过
        return JsonResponse({"status":"exist"})
    else:
        favourite = Favorites(
            user=user.user,
            literature=paper,
        )
        favourite.save()
    return JsonResponse({"status":"success"})

@login_required
def favourite_del(request):
    user = request.user.myuser if request.user.is_authenticated else None

    paper_id = request.GET.get('id')

    try:
        paper = Literature.objects.get(pk=paper_id)
    except:
        return JsonResponse({"status":"error"})

    favourite = Favorites.objects.filter(user=user.user,literature=paper)
    if len(favourite) > 0:
        favourite.delete()
    else:
        return JsonResponse({"status":"not_exist"})
        
    return JsonResponse({"status":"success"})

@login_required
def logout(request):
    auth.logout(request)
    return HttpResponseRedirect(reverse('root'))

def signup(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('homepage'))
    state = None
    form = RegisterForm()
    if request.method == 'POST':
        form = RegisterForm(request.POST)

        if form.is_valid():
            # print("ok")
            username = form.cleaned_data['username']
            name = form.cleaned_data['name']
            password = form.cleaned_data['password']
            repeat_password = form.cleaned_data['repeat_password']
            email = form.cleaned_data['email']
            if password == '' or repeat_password == '':
                state = 'empty'
            elif password != repeat_password:
                state = 'repeat_error'
            else:
                find = User.objects.filter(username=username)
                if len(find) == 0:
                    user = User.objects.create_user(username=username, password=password,email=email)
                    user.save()
                    new_my_user = MyUser(
                        user=user,
                        nickname=name,
                    )
                    new_my_user.save()
                    state = 'success'
                else:
                    state = 'user_exist'
        else:
            # print("no")
            state = 'verification_code_error'

    content = {
        'otype':'signup',
        'form': form,
        'state': state,
    }
    return render(request, 'backstage/index.html', content)

@login_required
def set_password_old(request):
    user = request.user
    state = None
    if request.method == 'POST':
        old_password = request.POST.get('old_password', '')
        new_password = request.POST.get('new_password', '')
        repeat_password = request.POST.get('repeat_password', '')
        if user.check_password(old_password):
            if not new_password:
                state = 'empty'
            elif new_password != repeat_password:
                state = 'repeat_error'
            else:
                user.set_password(new_password)
                user.save()
                state = 'success'
                user = None
                return HttpResponseRedirect(reverse('homepage'))
        else:
            state = 'password_error'
    content = {
        'user': user,
        'active_menu': 'set_password',
        'state': state,
    }

    return render(request, 'backstage/index.html', content)

def changepwd(request):
    return index(request)
    # user = request.user
    # state = None
    # form = ChangepwdForm()
    # if request.method == 'POST':
    #     form = ChangepwdForm(request.POST)

    #     if form.is_valid():
    #         old_password = form.cleaned_data['old_password']
    #         password = form.cleaned_data['password']
    #         repeat_password = form.cleaned_data['repeat_password']

    #         if user.check_password(old_password):
    #             if len(password)<6 or len(password)>64:
    #                 state = 'other_error'
    #             elif password != repeat_password:
    #                 state = 'repeat_error'
    #             else:
    #                 user.set_password(password)
    #                 user.save()
    #                 state = 'change_success'
    #                 user = None
    #         else:
    #             state = 'password_error'
    #     else:
    #         print("no")
    #         state = 'verification_code_error'

    # content = {
    #     'otype':'change',
    #     'form': form,
    #     'state': state,
    # }
    # if state == None and not user.is_authenticated:
    #     return HttpResponseRedirect(reverse('homepage'))

    # return render(request, 'backstage/index.html', content)

def recoverpwd(request):
    return index(request)
    # user = request.user if request.user.is_authenticated else None
    # if request.user.is_authenticated:
    #     return HttpResponseRedirect(reverse('homepage'))
    # state = None
    # form = RecoverpwdForm()
    # if request.method == 'POST':
    #     form = RecoverpwdForm(request.POST)

    #     if form.is_valid():
    #         # print("ok")
    #         username = form.cleaned_data['username']
    #         email = form.cleaned_data['email']
    #         try:
    #             user = User.objects.get(username=username)
    #         except:
    #             pass
    #         if user is not None:
    #             if user.email == email:
    #                 user.set_password(email)
    #                 user.save()
    #                 state = 'recover_success'
    #             else:
    #                 state = 'email_error'
    #         else:
    #             state = 'user_not_exist'
    #     else:
    #         # print("no")
    #         state = 'verification_code_error'

    # content = {
    #     'otype':'rec',
    #     'form': form,
    #     'state': state,
    # }
    # return render(request, 'backstage/index.html', content)
