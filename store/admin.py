from cdbazar.store.models import MediaType, Article, Item, Picture
from django.contrib import admin

class ItemAdmin(admin.ModelAdmin):
    list_display = ('article','commentary','barcode','packnumber','price', 'state_name','last_modified','to_store','home_page')
    list_filter = ('state','last_modified')
    pass
admin.site.register(Item, ItemAdmin)

class MediaAdmin(admin.ModelAdmin):
    list_display = ("name","desc","order")
    ordering = ('order','name')
admin.site.register(MediaType, MediaAdmin)

admin.site.register(Article)
admin.site.register(Picture)
