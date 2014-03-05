from django.conf.urls import patterns, include, url
from django.conf import settings

from cdbazar.views import ViewWithSubView, SearchView, AjaxDispatcher
from django.views.generic import TemplateView, ListView, DetailView, FormView, CreateView, UpdateView
from cdbazar import store
import store.views
import store.models

from cdbazar import eshop
import eshop.models
import eshop.views

# from cdbazar.store.views import ArticleList, ArticleUpdateView
# from cdbazar.store.models import Article, Picture
from cdbazar.accounts.views import UserProfileView
from cdbazar.flatpages.views import FlatPageEditView

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

# def forEshop(forEshop, forAdmin):
#     def handler(request, *args, **kwargs):
#         user = request.user
#         if user.is_authenticated() and user.has_perm('cdbazar.can_buy'):
#             return forAdmin(request, *args, **kwargs)
#         return forEshop(request, *args, **kwargs)
#     return handler

urlpatterns = patterns('',
                       # Examples:
                       url(r'^media/(?P<path>.*)$', 'django.views.static.serve', { 'document_root': settings.MEDIA_ROOT, }),
                       url(r'^accounts/profile', UserProfileView.as_view()),
                       url(r'^accounts/', include('registration.backends.default.urls')),
                       url(r'^(?P<pk>\d+)/$',      DetailView.as_view(model=store.models.Article)),
                       url(r'^(?P<pk>\d+)/edit/$', store.views.ArticleUpdateView.as_view(success_url="/store/article/")),
                       url(r'^store/', include('cdbazar.store.urls')),
                       url(r'^eshop/', include('cdbazar.eshop.urls')),
                       
                       # Uncomment the admin/doc line below to enable admin documentation:
                       url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

                       # Uncomment the next line to enable the admin:
                       url(r'^admin/', include(admin.site.urls)),
                       (r'^inplaceeditform/', include('inplaceeditform.urls')),
                       (r'^tinymce/', include('tinymce.urls')),
)

# staticke stranky
urlpatterns += patterns('django.contrib.flatpages.views',
                        url(r'^$',   'flatpage', {'url': '/'}, name='home-page'),
                        url(r'^o-nas/$',   'flatpage', {'url': '/o-nas/'}, name='about'),
                        #url(r'^o-nas/edit$', FlatPageEdit.as_view( url='/o-nas/'),
                        url(r'^licence/$', 'flatpage', {'url': '/licence/'}, name='license'),
                        url(r'^kontakt/$', 'flatpage', {'url': '/kontakt/'}, name='contact'),
)
                        
