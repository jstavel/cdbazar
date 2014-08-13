#-*- coding: utf-8 -*-
from django.db import models
from django.db import transaction
from cdbazar.store.models import Item, Article
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User
from decimal import Decimal
from collections import namedtuple
from django_extensions.db.fields import UUIDField
import datetime
from django.utils import timezone
from django.conf import settings

def calculateTotalPrice(items, additional_items):
    totalPrice = float(sum([ii.price for ii in items if ii.price])) \
        + float(sum([ii.price for ii in additional_items if ii.price]))
    return totalPrice

# polozka reprezentuje dodatecne polozky v kosiku
additionalItem = namedtuple('additionalItem',['desc','price','type','shortDesc'])

class Basket(object):
    BASKET_NAME="eshop-basket"

    def __init__(self,request):
        object.__init__(self)
        self.request = request
        self.additional_items = []
        if self.BASKET_NAME not in self.request.session:
            self.request.session[self.BASKET_NAME]=[]
            self.request.session.save()
            pass
        self._update()

    def _update(self):
        basket = self.request.session[self.BASKET_NAME]
        results = Item.objects.filter(id__in=basket, state=Item.state_for_sale)
        self.items = results
        self.additional_items = self.request.session.get('additional_items-for-' + self.BASKET_NAME,[])
        self.total = len(self.items)
        self.total_price = calculateTotalPrice(self.items, self.additional_items)
        return

    def addItem(self,item):
        results = Item.objects.filter(id__in=[item.id,] + [ii.id for ii in self.items], state=Item.state_for_sale)
        if results:
            self.request.session[self.BASKET_NAME]=[ii.id for ii in results]
            self.request.session.save()
            
            self.items = results
            self.total = len(self.items)
            self.total_price = calculateTotalPrice(self.items, self.additional_items)
        return

    def removeItem(self,item):
        basket = [ ii for ii in self.request.session[self.BASKET_NAME] if ii != item.id ]
        self.request.session[self.BASKET_NAME] = basket
        self.request.session.save()
        self._update()
        return
    
    def addAdditionalItem(self, item):
        self.additional_items.append(item)
        self.request.session['additional_items-for-' + self.BASKET_NAME] = self.additional_items
        self.request.session.save()
        self.total_price = calculateTotalPrice(self.items, self.additional_items)
        
    def removeAdditionalItem(self, toBeRemoved=lambda item: False):
        old_additional_items = self.additional_items
        self.additional_items = [ item for item in old_additional_items if not toBeRemoved(item) ]

    def articleInBasket(self,article_id):
        return article_id in [item.article_id for item in self.items]

    def getItemsForSale(self):
        return [ii for ii in self.items if ii.state == Item.state_for_sale]
            
    def sell(self):
        results = self.getItemsForSale()
        for item in results:
            item.state = Item.state_sold
            item.save()
        return results
            
DELIVERY_WAYS = (
    (1,_('Czech Post')),
    (2,_('DHL')),
    (3,_('Take at store')),
)

PAYMENT_WAYS = (
    (1,_('Pay at delivery')),
    (2,_('By bank account')),
    (3,_('Pay at store')),
)

class Order(models.Model):
    STATES = ( (1,'Waiting for payment'),
               (2,'Waiting for expedition'),
               (3,'Waiting for takeover'),
               (4,'Rejected'),
               (5,'Taken over'),
               )

    uuid = UUIDField()

    invoicing_firm = models.CharField(_('Firm'), max_length = 30, blank=True, null=True)
    invoicing_name = models.CharField(_('Name'), max_length = 30, default="")
    invoicing_surname = models.CharField(_('Surname'), max_length = 30, blank=True, null=True)
    invoicing_address_street = models.CharField(_("Street"), max_length = 30, default="")
    invoicing_address_zip = models.CharField(_("ZIP code"), max_length = 30, default="")
    invoicing_address_city = models.CharField(_("City"), max_length = 30, default="")
    invoicing_address_country = models.CharField(_("Country"), max_length = 30, blank=True, null=True)
    invoicing_address_ico = models.CharField(_("ICO"), max_length = 30, blank=True, null=True)
    invoicing_address_dic = models.CharField(_("VAT number"), max_length = 30, blank=True, null=True)
    
    contact_email = models.EmailField(_("Email"), max_length=30, default="")
    contact_phonenumber = models.CharField(_("Phone number"), max_length=30)
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

    created = models.DateTimeField(_("To store date of an item"), auto_now=True)

    state = models.PositiveSmallIntegerField(_("State"), choices=STATES, blank=True, null=True)

    def __unicode__(self):
        return u"Objednávka č.%d | cena: %d | zákazník: %s | ve stavu: %s" % (self.id,
                                                                              self.total_price,
                                                                              self.user,
                                                                              self.state_name)

    @property
    def total_price(self):
        #import sys,pdb; pdb.Pdb(stdout=sys.__stdout__).set_trace()
        items = self.orderitem_set.all()
        additional_items = self.orderadditionalitem_set.all()
        totalPrice = sum([ii.item.price for ii in items if ii.item.price] 
                         + [ii.price for ii in additional_items if ii.price])
        return totalPrice

    @classmethod
    def get_transitions(cls):
        return (
            ('Submit payment',    Order.state_waiting_for_payment),
            ('Submit expedition', Order.state_waiting_for_expedition),
            ('Submit takeover',   Order.state_waiting_for_takeover),
            ('Submit reject',   Order.state_waiting_for_takeover)
        )
        
    def processTransition(self, transitionName):
        fname = "transition_" + transitionName.lower().replace(' ','_')
        handler = getattr(self,fname,lambda: None)
        handler()

    def transition_submit_payment(self):
        print "submit payment transition"
        self.state=Order.state_waiting_for_expedition
        pass

    def transition_submit_expedition(self):
        print "submit payment transition"
        self.state=Order.state_waiting_for_takeover
        pass

    def transition_submit_takeover(self):
        print "submit takeover transition"
        self.state=Order.state_taken_over
        pass

    def available_transitions(self):
        return map(lambda tr: tr[0], filter(lambda transition: transition[1] == self.state, Order.TRANSITIONS))

    @property
    def state_name(self):
        return (map(lambda item: _(item[1]), filter(lambda tr: self.state == tr[0], self.STATES)) or ['Neznamy stav'])[0]

for state in Order.STATES:
    name = "state_" + state[1].lower().replace(" ","_")
    number = state[0]
    setattr(Order,name,number)

Order.TRANSITIONS = Order.get_transitions()    

class OrderItem(models.Model):
    order = models.ForeignKey(Order)
    item = models.ForeignKey(Item, default=Item())

class OrderAdditionalItem(models.Model):
    order = models.ForeignKey(Order)
    description = models.CharField(_("Description"), max_length = 256, blank=True, null=True)
    meta = models.CharField(_("Meta info"), max_length = 256, blank=True, null=True)
    price = models.DecimalField(_("Price"), decimal_places = 2, max_digits=10, default=Decimal("0"))

    def __unicode__(self):
        return u"%s | %d Kč" % (self.description, self.price)

class RandomManager(models.Manager):
    def get_queryset(self):
        return super(RandomManager, self).get_queryset().order_by("?")

class TradeAction(models.Model):
    """
    akce se zbozim, slevy
    """
    item = models.ForeignKey(Item, blank=True, null=True)
    discount = models.DecimalField(_("Discount [%]"), 
                                   decimal_places = 2, 
                                   max_digits = 10, 
                                   default=Decimal("0")
                                   )
    def __unicode__(self):
        return "sleva %s%% pro: " % (self.discount,) + unicode(self.item)

    objects = models.Manager()        
    random_set = RandomManager()
    

class DeliveryPrice(models.Model):
    delivery_way = models.PositiveSmallIntegerField(_("Delivery way"), choices=DELIVERY_WAYS, default=1)
    price = models.DecimalField(_("Price [CZK]"), decimal_places = 2, max_digits=10, default=Decimal("0"))
    
    def __unicode__(self):
        descs = [ii[1] for ii in DELIVERY_WAYS if ii[0] == self.delivery_way]
        desc = descs and descs[0] or ""
        return u"%s: %s Kč" % (desc, self.price)

    @classmethod
    def asAdditionalItemForBasket(cls,delivery_way):
        obj = cls.objects.get(delivery_way=delivery_way)
        descs = [ii[1] for ii in DELIVERY_WAYS if ii[0] == delivery_way]
        desc = descs and descs[0] or ""
        return additionalItem( price = obj.price,
                               desc = u"poplatek za doručení: " + desc,
                               shortDesc = desc,
                               type = "by-order:delivery")
                                
    @classmethod
    def asToBeRemovedFilter(cls):
        return lambda item: item.type == 'by-order:delivery'
        
class PaymentPrice(models.Model):
    payment_way = models.PositiveSmallIntegerField(_("Payment way"), choices=PAYMENT_WAYS, default=1)
    price = models.DecimalField(_("Price [CZK]"), decimal_places = 2, max_digits=10, default=Decimal("0"))
    
    def __unicode__(self):
        descs = [ii[1] for ii in PAYMENT_WAYS if ii[0] == self.payment_way]
        desc = descs and descs[0] or ""
        return u"%s: %s Kč" % (desc, self.price)
    
    @classmethod
    def asAdditionalItemForBasket(cls,payment_way):
        obj = cls.objects.get(payment_way=payment_way)
        descs = [ii[1] for ii in PAYMENT_WAYS if ii[0] == payment_way]
        desc = descs and descs[0] or ""
        return additionalItem(desc = u"poplatek za provedení platby: " + desc,
                              shortDesc = desc,
                              price = obj.price,
                              type = "by-order:payment")

    @classmethod
    def asToBeRemovedFilter(cls):
        return lambda item: item.type == 'by-order:payment'
    
class News(models.Model):
    title = models.CharField("Titulek", max_length=64)
    text = models.TextField(_("Text"))
    eshop = models.BooleanField("Vystavit na eshopu?", default=False)
    created = models.DateTimeField(_("To store date of an item"), auto_now=True)

class Content(models.Model):
    title = models.CharField("Titulek", max_length=64)
    text = models.TextField(_("Text"))
    eshop = models.BooleanField("Vystavit na eshopu?", default=False)
    created = models.DateTimeField(_("To store date of an item"), auto_now=True)
    contentType = models.CharField("Titulek", max_length=12)

class EmailMessage(models.Model):
    title = models.CharField("Titulek", max_length=64)
    text = models.TextField(_("Text"))
    created = models.DateTimeField(u'Vytvořeno', auto_now=True)

class Reservation(models.Model):
    query = models.CharField("dotaz", max_length=64)
    email = models.CharField("email", max_length=64)
    duemonths = models.IntegerField(u"na kolik měsíců platí", default = 6)
    created = models.DateTimeField(u"vytvořeno", auto_now=True)

    @property
    def active(self):
        now = datetime.datetime.now()
        if settings.USE_TZ:
            # For backwards compatibility, interpret naive datetimes in
            # local time. This won't work during DST change, but we can't
            # do much about it, so we let the exceptions percolate up the
            # call stack.

            default_timezone = timezone.get_default_timezone()
            now = timezone.make_aware(now, default_timezone)
            pass
        delta = now - self.created
        return delta.days <= (self.duemonths*30)

    @property
    def foundItems(self):
        return ['Article','Article']

    @property
    def numOfFoundItems(self):
        return len(self.foundItems)


class UserDiscount(models.Model):
    """
    slevy pro uzivatele na celou objednavku
    """
    user = models.ForeignKey(User)
    discount = models.DecimalField(_("User discount [%]"), 
                                   decimal_places = 2, 
                                   max_digits = 10, 
                                   default=Decimal("0")
                                   )
    def __unicode__(self):
        return u"věrnostní sleva %s%% pro: " % (self.discount,) + unicode(self.user)
