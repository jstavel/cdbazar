# -*- coding: utf-8 -*-
from django.utils.functional import SimpleLazyObject

def getMenu(request):
    def getMenuForBackend(request):
        return [ (u'Výkup','buyout', "/store/buyout/", ( (u"Na sklad","","/store/buyout/to-stock/",()),
                                                         (u"Na prodejnu","","/store/buyout/to-store/",()),
                                                         (u"K čištění","","/store/buyout/to-clean/",()),
                                                     )),
                 (u'Artikly', "articles", "/store/article/", ()),
                 (u'Zboží', "items", "/store/item/", ()),
                 (u'Akce',"actions", "/eshop/tradeaction/", ()),
                 (u'Objednávky', "orders", "/eshop/order/", ()),
                 (u"eShop", "eshop", "/eshop/", ()),
                 (u"Admin","admin","/admin/", ( 
                     (u"Stránky","","/admin/flatpages/flatpage/",()), 
                     (u"Novinky","","/admin/eshop/news/",()), 
                     (u"Šablony","","/admin/eshop/emailmessage/",()), 
                     (u"Média","","/admin/store/mediatype/",()), 
                     #(u"Kategorie","","/admin/store/category/",()), 
                 )),
             ]
        
    def getMenuForFrontend(request):
        return [ (u'O nás', "about", "/o-nas/", ()),
                 (u'Licence', "licence", "/licence/", ()),
                 (u'Kontakt', "contact", "/kontakt/", ()),
                 (u"eShop", "eshop", "/eshop/", ()),
             ]

    return request.user.has_perm('store.add_item') \
        and getMenuForBackend(request) \
        or getMenuForFrontend(request)
    
class Middleware(object):
    def process_request(self, request):
        request.menu = getMenu(request)
