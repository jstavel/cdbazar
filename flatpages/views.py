#-*- coding:utf-8 -*-
from django.views.generic import TemplateView, ListView, DetailView, UpdateView, CreateView, FormView
from django.db.models import Q
from django import forms
from django.forms.models import modelformset_factory
from django.shortcuts import render_to_response
from django.template import RequestContext, loader
from decimal import Decimal


class FlatPageEditView(TemplateView):
    template_name = "eshop/basket_review.html"
        
