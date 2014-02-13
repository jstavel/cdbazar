from django.conf.urls import patterns, include, url
from django.conf import settings
from cdbazar.eshop.views import *

# Uncomment the next two lines to enable the admin:
urlpatterns = patterns('',
                       url(r'^$',                  ArticleList.as_view()),
                       url(r'^item/(?P<pk>\d+)/add-tradeaction/$', AddTradeActionView.as_view()),
                       url(r'^item/(?P<pk>\d+)/from-basket/$',     FromBasketView.as_view()),
                       url(r'^article/(?P<pk>\d+)/to-basket/$',    ToBasketView.as_view()),
                       url(r'^tradeaction/$',                      TradeActionList.as_view()),
                       url(r'^tradeaction/(?P<pk>\d+)/delete/$',   TradeActionDelete.as_view()),
                       url(r'^basket/$',                           BasketView.as_view()),
                       url(r'^basket/update/$',                    BasketView.as_view()),
                       url(r'^order/(?P<pk>\d+)/$',               OrderView.as_view()),
                       url(r'^order/$',              OrderList.as_view()),
)
