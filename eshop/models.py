from django.db import models
from cdbazar.store.models import Item, Article
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User

def calculateTotalPrice(items):
    totalPrice = float(sum([ii.price for ii in items])) 
    return totalPrice

class Basket(object):
    BASKET_NAME="basket"
    def __init__(self,request):
        object.__init__(self)
        self.request = request
        
        if self.BASKET_NAME not in self.request.session:
            self.request.session[self.BASKET_NAME]=[]
            self.request.session.save()
            pass
        self._update()

    def _update(self):
        basket = self.request.session[self.BASKET_NAME]
        results = Item.objects.filter(id__in=basket, state=Item.state_for_sale)
        self.items = results
        self.total = len(self.items)
        self.total_price = calculateTotalPrice(self.items)
        return 

    def addItem(self,item):
        results = Item.objects.filter(id__in=[item.id,] + [ii.id for ii in self.items], state=Item.state_for_sale)
        if results:
            self.request.session[self.BASKET_NAME]=[ii.id for ii in results]
            self.request.session.save()
            
            self.items = results
            self.total = len(self.items)
            self.total_price = calculateTotalPrice(self.items)
        return

    def removeItem(self,item):
        basket = [ ii for ii in self.request.session[self.BASKET_NAME] if ii != item.id ]
        self.request.session[self.BASKET_NAME] = basket
        self.request.session.save()
        self._update()
        return
    
    def articleInBasket(self,article_id):
        return article_id in [item.article_id for item in self.items]

    def sell(self):
        with transaction.commit_on_success():
            results = [ii for ii in self.items if ii.state == Item.state_for_sale]
            for item in results:
                item.state = Item.state_sold
                item.save()
            return results
                
DELIVERY_WAYS = (
    (1,_('Czech Post')),
    (2,_('DHL')),
    (3,_('At store')),
)

PAYMENT_WAYS = (
    (1,_('Pay at delivery')),
    (2,_('By bank account')),
    (3,_('At store')),
)

class Order(models.Model):
    invoicing_firm = models.CharField(_('Firm'), max_length = 30, blank=True, null=True )
    invoicing_name = models.CharField(_('Name'), max_length = 30, blank=True, null=True)
    invoicing_surname = models.CharField(_('Surname'), max_length = 30, blank=True, null=True)
    invoicing_address_street = models.CharField(_("Street"), max_length = 30, blank=True, null=True)
    invoicing_address_zip = models.CharField(_("ZIP code"), max_length = 30, blank=True, null=True)
    invoicing_address_city = models.CharField(_("City"), max_length = 30, blank=True, null=True)
    invoicing_address_country = models.CharField(_("Country"), max_length = 30, blank=True, null=True)
    invoicing_address_ico = models.CharField(_("ICO"), max_length = 30, blank=True, null=True)
    invoicing_address_dic = models.CharField(_("VAT number"), max_length = 30, blank=True, null=True)
    
    contact_email = models.EmailField(_("Email"), max_length=30, blank=True, null=True)
    contact_phonenumber = models.CharField(_("Phone number"), max_length=30, blank=True, null=True)
    user = models.ForeignKey(User, blank=True, null=True)

    delivery_way = models.PositiveSmallIntegerField(_("Delivery way"), choices=DELIVERY_WAYS, default=1)

    delivery_is_the_same_as_invoicing = models.BooleanField(_("Delivery address is the same as invoicing address"), default=True)
    delivery_firm = models.CharField(_('Firm'), max_length = 30, blank=True, null=True )
    delivery_name = models.CharField(_('Name'), max_length = 30, blank=True, null=True)
    delivery_surname = models.CharField(_('Surname'), max_length = 30, blank=True, null=True )
    delivery_address_street = models.CharField(_("Street"), max_length = 30, blank=True, null=True)
    delivery_address_zip = models.CharField(_("ZIP code"), max_length = 30, blank=True, null=True)
    delivery_address_city = models.CharField(_("City"), max_length = 30, blank=True, null=True)
    delivery_address_country = models.CharField(_("Country"), max_length = 30, blank=True, null=True)

    payment_way = models.PositiveSmallIntegerField(_("Payment way"), choices=PAYMENT_WAYS, default=1)


class OrderItem(models.Model):
    order = models.ForeignKey(Order)
    
