from .models import Order, OrderItem, OrderAdditionalItem, DeliveryPrice, PaymentPrice, TradeAction, News, Content
from django.contrib import admin

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
