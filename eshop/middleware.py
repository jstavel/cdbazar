# -*- coding: utf-8 -*-
from django.contrib import auth
from django.core.exceptions import ImproperlyConfigured
from django.utils.functional import SimpleLazyObject
from .models import TradeAction, Article, News, Order

def getActions(request):
    return TradeAction.objects.all().order_by("?")[:20]

def getNewArticles(request):
    return Article.objects.all().order_by("to_store")[:20]

def getNews(request):
    return News.objects.all().order_by('created')[:5]

def getMyOrders(request):
    if request.user.is_authenticated():
        return Order.objects.filter(user=request.user)
    return []

def getBasket(request):
    pass

class Middleware(object):
    def process_request(self, request):
        request.tradeActions = getActions(request)
        request.newArticles = getNewArticles(request)
        request.news = getNews(request)
        request.orderTransitions = Order.TRANSITIONS
        request.orderStates = Order.STATES
        request.myOrders = getMyOrders(request)
        #request.basket = getBasket(request)
