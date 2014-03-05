# -*- coding: utf-8 -*-
from django.contrib import auth
from django.core.exceptions import ImproperlyConfigured
from django.utils.functional import SimpleLazyObject
from .models import MediaType

def getMediaTypes(request):
    return MediaType.objects.all()

class Middleware(object):
    def process_request(self, request):
        request.mediaTypes = getMediaTypes(request)
