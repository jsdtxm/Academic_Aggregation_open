from django.conf.urls import url
from mainapp import views

urlpatterns = [
    url('^$', views.index, name='root'),
    url('^about/$', views.about, name='about'),

    url('^login/$', views.login, name='login'),
    url('^signup/$', views.signup, name='signup'),
    url('^shop/$', views.shop, name='shop'),
    url('^contact/$', views.contact, name='contact'),
    url('^shop_list/$', views.shop_list, name='shop_list'),
    url('^single_product/$', views.single_product, name='single_product'),
]
