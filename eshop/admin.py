# -*- coding: utf-8 -*-
from .models import (
    Order, 
    OrderItem, 
    OrderAdditionalItem,
    DeliveryPrice, 
    PaymentPrice, 
    TradeAction,
    News, 
    Content,
    EmailMessage,
    Reservation,
    UserDiscount,
)
from django.contrib import admin
from django import forms
from django.core.urlresolvers import reverse
from django.contrib.flatpages.admin import FlatPageAdmin
from django.contrib.flatpages.models import FlatPage
from tinymce.widgets import TinyMCE
from django.http import Http404, HttpResponse, HttpResponseRedirect

admin.site.register(DeliveryPrice)
admin.site.register(PaymentPrice)
admin.site.register(TradeAction)

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    readonly_items = ('item',)
        

class OrderAdditionalItemInline(admin.TabularInline):
    model = OrderAdditionalItem

class OrderAdmin(admin.ModelAdmin):
    inlines = [
        # OrderItemInline,
        OrderAdditionalItemInline
    ]

admin.site.register(Order, OrderAdmin)

class NewsAdmin(admin.ModelAdmin):
    list_display = ('title','created', 'eshop')
    pass

admin.site.register(News, NewsAdmin)

class ContentAdmin(admin.ModelAdmin):
    list_display = ('title','contentType','created', 'eshop')
    pass

admin.site.register(Content, ContentAdmin)

class ReservationAdmin(admin.ModelAdmin):
    list_display = ('query','email','active','numOfFoundItems','created','duemonths')
    list_filter = ('created',)
    pass

admin.site.register(Reservation, ReservationAdmin)

class TinyMCEFlatPageAdmin(FlatPageAdmin):
    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'content':
            return db_field.formfield(widget=TinyMCE(
                attrs={'cols': 80, 'rows': 30},
                mce_attrs={'external_link_list_url': reverse('tinymce.views.flatpages_link_list')},
            ))
        return super(TinyMCEFlatPageAdmin, self).formfield_for_dbfield(db_field, **kwargs)

admin.site.unregister(FlatPage)
admin.site.register(FlatPage, TinyMCEFlatPageAdmin)

class EmailMessageAdmin(admin.ModelAdmin):
    list_display = ('title',)
    pass

admin.site.register(EmailMessage, EmailMessageAdmin)

from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin

admin.site.unregister(User)

from .models import additionalItem

class UserOrderInline(admin.TabularInline):
    model = Order
    extra = 0
    fields = ('invoicing_firm','state')

class UserDiscountInline(admin.TabularInline):
    model = UserDiscount
    extra = 0

def getUserDiscount(user):
    discounts =[dd.discount for dd in user.userdiscount_set.all()] 
    return discounts and sum(discounts) or 0

def getUserDiscountAsAdditionalItem(user, price):
    discount = user.getUserDiscount()
    return additionalItem( price = price,
                           shortDesc = u"věrnostní sleva",
                           desc = u"věrnostní sleva",
                           type = "by-order:user-discount" )

def numOfCancelledOrders(user):
    return Order.objects.filter(user=user).filter(state=Order.state_rejected).count()

def numOfPaidOrders(user):
    return Order.objects.filter(user=user).exclude(state=Order.state_rejected).exclude(state=Order.state_waiting_for_payment).count()

User.getUserDiscount = getUserDiscount
User.getUserDiscountAsAdditionalItem = getUserDiscountAsAdditionalItem
User.numOfCancelledOrders = numOfCancelledOrders
User.numOfPaidOrders = numOfPaidOrders

class NewUserAdmin(UserAdmin):
    inlines = (UserDiscountInline,)
    list_display = UserAdmin.list_display + ('getUserDiscount',)

    def response_post_save_change(self, request, obj):
        """
        Figure out where to redirect after the 'Save' button has been pressed
        when editing an existing object.
        """
        opts = self.model._meta
        post_url_arg=request.REQUEST.get('post_url_arg')
        post_url = request.REQUEST.get('post_url')
        if post_url:
            return HttpResponseRedirect(post_url_arg and "%s?%s" % (post_url, post_url_arg) or post_url)
        if self.has_change_permission(request, None):
            post_url = reverse('admin:%s_%s_changelist' %
                               (opts.app_label, opts.module_name),
                               current_app=self.admin_site.name)
        else:
            post_url = reverse('admin:index',
                               current_app=self.admin_site.name)
        return HttpResponseRedirect(request.REQUEST.get('post_url') or post_url)

admin.site.register(User,NewUserAdmin)


