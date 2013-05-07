from django.conf.urls import patterns, include, url
from django.conf import settings

from cdbazar.views import ViewWithSubView, SearchView, AjaxDispatcher
from django.views.generic import TemplateView, ListView, DetailView, FormView, CreateView, UpdateView
from cdbazar.store.views import ArticleList, ArticleUpdateView
from cdbazar.store.models import Article, Picture

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
                       # Examples:
                       url(r'^media/(?P<path>.*)$', 'django.views.static.serve', { 'document_root': settings.MEDIA_ROOT, }),
                       
                       url(r'^(?P<pk>\d+)/$',      DetailView.as_view(model=Article)),
                       url(r'^(?P<pk>\d+)/edit/$', ArticleUpdateView.as_view(success_url="/store/article/")),
                       url(r'^$',ArticleList.as_view(paginate_by=10)),
                       url(r'^store/', include('cdbazar.store.urls')),
                       url(r'^eshop/', include('cdbazar.eshop.urls')),
                       
                       # Uncomment the admin/doc line below to enable admin documentation:
                           url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
                       
                       # Uncomment the next line to enable the admin:
                           url(r'^admin/', include(admin.site.urls)),
)
