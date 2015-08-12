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
from cdbazar.eshop.models import Order

class UserProfileView(TemplateView):
    template_name = "accounts/profile.html"

    def get_context_data(self,**kwargs):
        user = self.request.user
        userProfile, created = UserProfile.objects.get_or_create(user=user)  
        if created:
            userProfile.save()

        context = TemplateView.get_context_data(self,**kwargs)
        context['my_orders'] = Order.objects.filter(user=user)
        context['form_authentication'] = getattr(self,'form_authentication',
                                                 UserProfileAuthenticationForm())
        context['form_contact'] = getattr(self,'form_contact',
                                          UserProfileContactForm(instance=userProfile))
        context['form_invoicing'] = getattr(self,'form_invoicing',
                                            UserProfileInvoicingForm(instance=userProfile))
        context['form_delivery'] = getattr(self,'form_delivery',
                                           UserProfileDeliveryForm(instance=userProfile))
        context['form_payment'] = getattr(self,'form_payment',
                                          UserProfilePaymentForm(instance=userProfile))
        return context

    def post(self,request, *args, **kwargs):
        self.form_authentication =UserProfileAuthenticationForm(request.POST)

        if self.form_authentication.is_valid():
            self.form_authentication.save(user=self.request.user)

        for form_name, form in (('form_contact',UserProfileContactForm(request.POST)),
                                ('form_invoicing',UserProfileInvoicingForm(request.POST)),
                                ('form_delivery',UserProfileDeliveryForm(request.POST)),
                                ('form_payment',UserProfilePaymentForm(request.POST))):
            if form.is_valid():
                form.save()
            setattr(self,form_name,form)

        return self.get(request, *args, **kwargs)
