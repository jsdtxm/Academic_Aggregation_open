from django import forms
from captcha.fields import CaptchaField
 
#auth_form v1.0

class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-username form-control','placeholder':"用户名..."}),
        max_length=32,
        required=True,
        error_messages={'required': '用户名不能为空'},
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-password form-control','placeholder':"密码..."}),
        max_length=64,
        min_length=6,
        required=True,
        error_messages={'required': '密码不能为空'},
    )
    captcha = CaptchaField(error_messages={"invalid": "验证码错误"})

class RegisterForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-username form-control','placeholder':"用户名..."}),
        max_length=32,
        required=True,
        error_messages={'required': '用户名不能为空'},
    )
    name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-username form-control','placeholder':"姓名..."}),
        max_length=32,
        required=True,
        error_messages={'required': '姓名不能为空'},
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-password form-control','placeholder':"密码..."}),
        max_length=64,
        min_length=6,
        required=True,
        error_messages={'required': '密码不能为空'},
    )
    repeat_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-password form-control','placeholder':"重复密码..."}),
        max_length=64,
        min_length=6,
        required=True,
        error_messages={'required': '重复密码不能为空'},
    )
    email = forms.EmailField(
        widget=forms.TextInput(attrs={'class': 'form-password form-control','placeholder':"邮箱..."}),
        max_length=64,
        required=True,
        error_messages={'required': '邮箱不能为空'},
    )
    captcha = CaptchaField(error_messages={"invalid": "验证码错误"})

class ChangepwdForm(forms.Form):
    old_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-password form-control','placeholder':"原密码..."}),
        max_length=64,
        min_length=6,
        required=True,
        error_messages={'required': '密码不能为空'},
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-password form-control','placeholder':"新密码..."}),
        max_length=64,
        min_length=6,
        required=True,
        error_messages={'required': '密码不能为空'},
    )
    repeat_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-password form-control','placeholder':"重复新密码..."}),
        max_length=64,
        min_length=6,
        required=True,
        error_messages={'required': '重复密码不能为空'},
    )
    captcha = CaptchaField(error_messages={"invalid": "验证码错误"})

class RecoverpwdForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-username form-control','placeholder':"用户名..."}),
        max_length=32,
        required=True,
        error_messages={'required': '用户名不能为空'},
    )
    email = forms.EmailField(
        widget=forms.TextInput(attrs={'class': 'form-password form-control','placeholder':"邮箱..."}),
        max_length=64,
        required=True,
        error_messages={'required': '邮箱不能为空'},
    )
    captcha = CaptchaField(error_messages={"invalid": "验证码错误"})

    