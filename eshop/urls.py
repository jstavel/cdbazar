from django.conf.urls import patterns, include, url
from django.conf import settings
from cdbazar.eshop.views import *

# Uncomment the next two lines to enable the admin:
urlpatterns = patterns('',
                       url(r'^$',                  ArticleList.as_view()),
                       url(r'^item/(?P<pk>\d+)/from-basket/$', FromBasketView.as_view()),
                       url(r'^article/(?P<pk>\d+)/to-basket/$', ToBasketView.as_view()),
                       url(r'^basket/$',                   BasketView.as_view()),
                       url(r'^order/(?P<pk>\d+)/$',        OrderView.as_view()),
)
