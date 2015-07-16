from django.conf.urls import patterns, include, url
from cdbazar.views import ViewWithSubView, SearchView, AjaxDispatcher
from django.views.generic import TemplateView, ListView, DetailView, FormView, CreateView, UpdateView
from .views import *
from .models import Article, Picture, Item
from django.contrib.auth.decorators import login_required, permission_required
p = permission_required('store.add_item')

urlpatterns = patterns('',
                       url(r'^sell/$',                     p(SellView.as_view())),
                       url(r'^basket/$',                   p(BasketView.as_view())),
                       url(r'^buyout/$',                   p(BuyoutView.as_view())),
                       url(r'^buyout/to-stock/$',          p(BuyoutToStockView.as_view())),
                       url(r'^buyout/to-store/$',          p(BuyoutToStoreView.as_view())),
                       url(r'^buyout/to-clean/$',          p(BuyoutToCleanView.as_view())),
                       url(r'^buyout/lookup/$',            p(BuyoutLookupView.as_view())),
                       url(r'^buyout/load-detail/$',       p(BuyoutLoadDetailView.as_view())),
                       url(r'^item/(?P<pk>\d+)/$',         p(DetailView.as_view(model=Item))),
                       url(r'^item/(?P<pk>\d+)/edit/$',    p(ItemUpdateView.as_view(success_url="/store/item/"))),
                       url(r'^item/(?P<pk>\d+)/to-basket/$', p(ToBasketView.as_view())),
                       url(r'^item/(?P<pk>\d+)/from-basket/$', p(FromBasketView.as_view())),
                       url(r'^item/(?P<pk>\d+)/edit/(?P<field>\w+)/$',    p(ItemFieldUpdateView.as_view())),
                       url(r'^item/$',                     p(ItemList.as_view())),
                       url(r'^article/(?P<pk>\d+)/edit/$', p(ArticleUpdateView.as_view(success_url="/store/article/"))),
                       url(r'^article/(?P<pk>\d+)/load-picture/$', p(ArticlePictureLoadView.as_view())),

                       url(r'^article/(?P<pk>\d+)/$',      p(ArticleDetailView.as_view())),
                       url(r'^article/add/$',              p(ArticleCreateView.as_view())),
                       url(r'^article/$',                  p(ArticleList.as_view())),
                       url(r'^mediatype/add/$',            p(MediaTypeCreateView.as_view(success_url="/store/item/"))),
                       url(r'^picture/(?P<pk>\d+)/$',      p(DetailView.as_view(model=Picture))),
                       url(r'^picture/$',                  p(ListView.as_view(model=Picture, paginate_by=50))),
                       )
                       
