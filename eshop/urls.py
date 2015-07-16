from django.conf.urls import patterns, include, url
from django.conf import settings
from cdbazar.eshop.views import *
from django.contrib.auth.decorators import login_required, permission_required
p = permission_required('store.add_item')

# Uncomment the next two lines to enable the admin:
urlpatterns = patterns('',
                       url(r'^$',                        EShopList.as_view()),
                       url(r'^articles/$',               ArticleList.as_view()),
                       url(r'^articles-shortly/$',       ArticleListShortly.as_view()),
                       url(r'^articles-with-tradeaction/$',       ArticleListWithTradeAction.as_view()),
                       url(r'^article/(?P<pk>\d+)/$',    ArticleDetail.as_view()),
                       url(r'^item/(?P<pk>\d+)/add-tradeaction/$', AddTradeActionView.as_view()),
                       url(r'^item/(?P<pk>\d+)/from-basket/$',     FromBasketView.as_view()),
                       url(r'^article/(?P<pk>\d+)/to-basket/$',    ToBasketView.as_view()),
                       url(r'^tradeaction/$',                      TradeActionList.as_view()),
                       url(r'^tradeaction/(?P<pk>\d+)/delete/$',   TradeActionDelete.as_view()),
                       url(r'^basket/$',                           BasketView.as_view()),
                       url(r'^basket/update/$',                    BasketView.as_view()),
                       url(r'^order/(?P<pk>\d+)/$',                OrderView.as_view()),
                       url(r'^order/(?P<pk>\d+)/pdf/$',            get_order_pdf),
                       url(r'^ajax/emailmessage/(?P<pk>\d+)/$',    EmailMessageView.as_view()),
                       url(r'^order/$',              p(OrderList.as_view())),
                       )
