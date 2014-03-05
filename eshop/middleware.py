# -*- coding: utf-8 -*-
from django.contrib import auth
from django.core.exceptions import ImproperlyConfigured
from django.utils.functional import SimpleLazyObject
from .models import TradeAction, Article, News

def getActions(request):
    return TradeAction.objects.all().order_by("?")[:20]

def getNewArticles(request):
    return Article.objects.all().order_by("to_store")[:20]

def getNews(request):
    return News.objects.all().order_by('created')[:5]

class Middleware(object):
    def process_request(self, request):
        request.tradeActions = getActions(request)
        request.newArticles = getNewArticles(request)
        request.news = getNews(request)
            
