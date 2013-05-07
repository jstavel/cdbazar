from django.conf.urls import patterns, include, url
from cdbazar.views import ViewWithSubView, SearchView, AjaxDispatcher
from django.views.generic import TemplateView, ListView, DetailView, FormView, CreateView, UpdateView
from .views import *
from .models import Article, Picture, Item

urlpatterns = patterns('',
                       url(r'^sell/$',                     SellView.as_view()),
                       url(r'^basket/$',                   BasketView.as_view()),
                       url(r'^buyout/$',                   BuyoutView.as_view()),
                       url(r'^buyout/to-stock/$',          BuyoutToStockView.as_view()),
                       url(r'^buyout/to-store/$',          BuyoutToStoreView.as_view()),
                       url(r'^buyout/to-clean/$',          BuyoutToCleanView.as_view()),
                       url(r'^buyout/lookup/$',            BuyoutLookupView.as_view()),
                       url(r'^item/(?P<pk>\d+)/$',         DetailView.as_view(model=Item)),
                       url(r'^item/(?P<pk>\d+)/edit/$',    ItemUpdateView.as_view(success_url="/store/item/")),
                       url(r'^item/(?P<pk>\d+)/to-basket/$', ToBasketView.as_view()),
                       url(r'^item/(?P<pk>\d+)/from-basket/$', FromBasketView.as_view()),
                       url(r'^item/(?P<pk>\d+)/edit/(?P<field>\w+)/$',    ItemUpdateView.as_view(success_url="/store/item/")),
                       url(r'^item/$',                     ItemList.as_view()),
                       url(r'^article/(?P<pk>\d+)/edit/$', ArticleUpdateView.as_view(success_url="/store/article/")),
                       url(r'^article/(?P<pk>\d+)/$',      DetailView.as_view(model=Article)),
                       url(r'^article/add/$',              ArticleCreateView.as_view()),
                       url(r'^article/$',                  ArticleList.as_view()),
                       url(r'^mediatype/add/$',            MediaTypeCreateView.as_view(success_url="/store/item/")),
                       url(r'^picture/(?P<pk>\d+)/$',      DetailView.as_view(model=Picture)),
                       url(r'^picture/$',                  ListView.as_view(model=Picture, paginate_by=50)),
                       )
