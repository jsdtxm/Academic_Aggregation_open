from django.conf.urls import url
from backstage import views

urlpatterns = [
    url('^$', views.index, name='index'),
    url('^profile/$', views.profile, name='profile'),
    url('^source_list/$', views.source_list, name='source_list'),
    url('^logout/',views.logout,name="logout"),
    url('^changepwd/$', views.changepwd, name='changepwd'),
    url('^recoverpwd/$', views.recoverpwd, name='recoverpwd'),
    url('^favourite_list/$', views.favourite_list, name='favourite_list'),
    url('^favourite_paper/$', views.favourite_paper, name='favourite_paper'),
    url('^favourite_del/$', views.favourite_del, name='favourite_del'),
    url('^pdf_view/$', views.pdf_view, name='pdf_view'),
    url('^banner/$', views.recoverpwd, name='forum_list'),
    url('^detail/$', views.detail, name='detail'),

    url('^test/$', views.test, name='test'),
    url('^test2/$', views.test2, name='test2'),
    
    
]
