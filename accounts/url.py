from django.conf.urls import patterns, include, url
from django.conf import settings
from cdbazar.accounts.views import *

# Uncomment the next two lines to enable the admin:
urlpatterns = patterns('',
                       url(r'^profile/$',                   UserProfileView.as_view()),
)
