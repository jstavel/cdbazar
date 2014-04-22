from .models import (
    Order, 
    OrderItem, 
    OrderAdditionalItem,
    DeliveryPrice, 
    PaymentPrice, 
    TradeAction,
    News, 
    Content,
    EmailMessage
)
from django.contrib import admin
from django import forms
from django.core.urlresolvers import reverse
from django.contrib.flatpages.admin import FlatPageAdmin
from django.contrib.flatpages.models import FlatPage
from tinymce.widgets import TinyMCE

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
