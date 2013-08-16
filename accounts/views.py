# Create your views here.
from django.views.generic import TemplateView, ListView, DetailView, UpdateView, CreateView, FormView
from django.db.models import Q
from django import forms
from django.forms.models import modelformset_factory
from django.shortcuts import render_to_response
from django.template import RequestContext, loader
from django.contrib.auth.models import User
from .models import UserProfile
from .forms import *
from cdbazar.store.models import MediaType

class UserProfileView(TemplateView):
    template_name = "accounts/profile.html"

    def get_context_data(self,**kwargs):
        context = TemplateView.get_context_data(self,**kwargs)
        context['mediatypes'] = MediaType.objects.all()
        context['form_authentication'] = UserProfileAuthenticationForm()
        context['form_invoicing'] = UserProfileInvoicingForm()
        context['form_delivery'] = UserProfileDeliveryForm()
        context['form_payment'] = UserProfilePaymentForm()
        return context
