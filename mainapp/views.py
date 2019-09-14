from django.contrib import auth
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from requests_html import HTML, HTMLSession

from mainapp.models import MyUser

from .auth_form import ChangepwdForm, LoginForm, RecoverpwdForm, RegisterForm

# Create your views here.

def index(request):
    user = request.user if request.user.is_authenticated else None

    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('index'))
        
    content = {
        'active_menu': 'index',
        'user': user,
    }
    return render(request, 'mainapp/index.html', content)

def shop(request):
    user = request.user if request.user.is_authenticated else None
    content = {
        'active_menu': 'shop',
        'user': user,
    }
    return render(request, 'mainapp/shop.html', content)

def contact(request):
    user = request.user if request.user.is_authenticated else None
    content = {
        'active_menu': 'contact',
        'user': user,
    }
    return render(request, 'mainapp/contact.html', content)

def about(request):
    user = request.user if request.user.is_authenticated else None
    content = {
        'active_menu': 'about',
        'user': user,
    }
    return render(request, 'mainapp/about.html', content)

def shop_list(request):
    user = request.user if request.user.is_authenticated else None
    content = {
        'active_menu': 'shop_list',
        'user': user,
    }
    return render(request, 'mainapp/shop_list.html', content)

def TencentCaptcha(request):
    '''腾讯验证码验证函数'''
    if request.META.get('HTTP_X_FORWARDED_FOR'):
        ip =  request.META['HTTP_X_FORWARDED_FOR']
    else:
        ip = request.META['REMOTE_ADDR']
    
    try:
        url = 'https://ssl.captcha.qq.com/ticket/verify/?aid=2094639739&AppSecretKey=04fG9GWVEx-fshMG5Tk0PXg**&Ticket=' + request.POST['ticket'] + '&Randstr='+ request.POST['randstr'] + '&UserIP=' + ip         
        session = HTMLSession()
        r = session.get(url).json()
        print(r)
    except:
        return False

    if r['response'] != '1' or int(r['evil_level']) > 50:
        # 验证错误，弹出
        return False

    return True

def login(request):
    user = request.user if request.user.is_authenticated else None

    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('index'))

    state = None
    form = LoginForm()

    if request.method == 'POST':
        if not TencentCaptcha(request):
            state = 'Blocked by Tencent Protect'

        else:
            form = LoginForm(request.POST)

            if form.is_valid():
                # print("ok")
                username = form.cleaned_data['username']
                password = form.cleaned_data['password']
                user = auth.authenticate(username=username, password=password)
                if user is not None:
                    auth.login(request, user)
                    return HttpResponseRedirect(reverse('root'))
                else:
                    state = 'not_exist_or_password_error'
            else:
                # print("no")
                state = 'verification_code_error'

    content = {
        'otype':'login',
        'form': form,
        'state': state,
    }
    return render(request, 'mainapp/login.html', content)

def signup(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('index'))
    state = None
    form = RegisterForm()
    if request.method == 'POST':
        
        if not TencentCaptcha(request):
            state = 'verification_code_error'

        else:
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
    return render(request, 'mainapp/signup.html', content)


def single_product(request):
    user = request.user if request.user.is_authenticated else None
    content = {
        'active_menu': 'single_product',
        'user': user,
    }
    return render(request, 'mainapp/single_product.html', content)
