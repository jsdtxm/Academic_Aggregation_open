from django.db import models
from django.utils.timezone import now
from django.contrib.auth.models import User

class Department(models.Model):
    #部门
    name = models.CharField('部门名', max_length=30)
    process = models.IntegerField('过程', default=1)
    sort = models.IntegerField('排序', default=0)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['sort']
        get_latest_by = 'sort'
        verbose_name = "部门"
        verbose_name_plural = verbose_name


class MyUser(models.Model):
    #用户
    role = (
        (0, '普通用户'),
        (1, '审核用户'),
        (2, '管理用户'),
    )
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    nickname = models.CharField('姓名',max_length=16)
    department = models.ForeignKey(Department, verbose_name='单位', on_delete=models.CASCADE,null=True,blank=True)
    status = models.SmallIntegerField(choices=role, default=0, verbose_name='角色')

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = "用户"
        verbose_name_plural = verbose_name

class Literature(models.Model):
    #文献

    ltypes = (
        (0, '期刊'),
        (1, '学位'),
        (2, '图书'),
        (3, '会议'),
        (4, '专利'),
    )

    langs = (
        (0, '中文'),
        (1, '英文'),
        (2, '其他'),
    )

    language = models.SmallIntegerField(choices=langs, default=0, verbose_name='语言')
    ltype = models.SmallIntegerField(choices=ltypes, default=0, verbose_name='文献类型')
    title = models.CharField('题名', max_length=256,null=True)
    authors = models.CharField('作者', max_length=256,null=True,blank=True)
    publish =  models.CharField('来源', max_length=256,null=True,blank=True)
    doi = models.CharField('数字对象唯一标识符', max_length=128,null=True,blank=True)
    institution = models.CharField('机构', max_length=256,null=True,blank=True)
    sore_year = models.IntegerField('发表年度',null=True,blank=True)
    cited = models.IntegerField('被引',null=True,blank=True)
    abstract = models.TextField('摘要',null=True,blank=True)
    keywords = models.CharField('关键词',max_length=256,null=True,blank=True)
    ai_keyword = models.CharField('AI关键词',max_length=256,null=True,blank=True)
    quotes = models.TextField('参考文献',null=True,blank=True)
    sc_quote =  models.TextField('GB引用',null=True,blank=True)

    upload_date = models.DateTimeField('上传时间', default=now)
    creater = models.ForeignKey(MyUser, verbose_name='创建者', on_delete=models.CASCADE,null=True,blank=True)

    paperid = models.CharField('百度学术id',null=True,blank=True, max_length=256)
    cnki_info = models.CharField('中国知网数据',null=True,blank=True, max_length=512)
    source_url = models.CharField('主来源URL',null=True,blank=True, max_length=512)
    page = models.CharField('页码',null=True,blank=True, max_length=512)
    
    all_version = models.TextField('全部来源',null=True,blank=True)
    savelink = models.TextField('下载链接',null=True,blank=True)
    #文件
    upfile = models.FileField(upload_to='upload/%Y/%m/%d/',null=True,blank=True)

    collect_from = models.CharField('收集来源',null=True,blank=True, max_length=128)
    detailed = models.BooleanField('已处理', default=False)
    weight = models.IntegerField('权值', default=0,null=True,blank=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-upload_date']
        verbose_name = "文献"
        verbose_name_plural = verbose_name
        get_latest_by = '-upload_date'

class Favorites(models.Model):
    #收藏夹
    user = models.ForeignKey(User, verbose_name='用户',on_delete=models.CASCADE)
    literature = models.ForeignKey(Literature, verbose_name='文献',on_delete=models.CASCADE)
    show = models.BooleanField('是否显示',default=True)
    ontop = models.BooleanField('是否置顶',default=False)
    star_level = models.IntegerField('星级', default=0)
    upload_date = models.DateTimeField('上传时间', default=now)

    def __str__(self):
        return self.user.username

    class Meta:
        ordering = ['-upload_date']
        verbose_name = "收藏夹"
        verbose_name_plural = verbose_name