# -*- coding: utf-8 -*-
from django.db import models, transaction, connection
from django.utils.translation import ugettext_lazy as _, ugettext
from datetime import datetime
from history.models import HistoricalRecords
from django.template.defaultfilters import slugify
from django.contrib.auth.models import User
from django_extensions.db.models import TimeStampedModel

# Create your models here.

ARTICLE_TYPES = (
    ('CD','CD'),
    ('SA CD','SA CD'),
    ('DVD','DVD'),
    ('DVD audio','DVD audio'),
    ('Playstation 2','Playstation 2'),
    ('Playstation 3','Playstation 3'),
    ('XBox 360','XBox 360'),
    ('PC hry','PC hry'),
    ('Blu-Ray disk','Blu-Ray disk'),
    ('PSP','PSP'),
    )

class MediaType(models.Model):
    name = models.CharField(_("Name"), max_length=16, db_index=True, unique=True)
    desc = models.CharField(_("Description"), max_length=48, blank=True)
    
    def normalized_key (self):
        return slugify(self.key)

    def __unicode__(self):
        return u"%s" % (self.name,)

# Create your models here.
class Picture(models.Model):
    class Meta:
        verbose_name = _('picture')
        verbose_name_plural = _('Pictures')
        
    img = models.ImageField(upload_to="img/articles", max_length="2048")

    def __unicode__(self):
        return unicode(self.img)
        
class ForEShopManager(models.Manager):
    def get_queryset(self):
        return super(ForEShopManager, self).get_queryset().filter(eshop=True)

class AtActionManager(models.Manager):
    def get_queryset(self):
        return super(AtActionManager, self).get_queryset().filter(eshop=True)

class Article(models.Model):
    title = models.CharField(_('Title'),max_length=222)
    interpret = models.CharField(_("Interpret"), max_length=64, blank=True, null=True)
    year = models.IntegerField(_("Year"), blank=True, null=True)
    publisher = models.CharField(_('Publisher'),max_length=64, blank=True)
    mediaType = models.ForeignKey(MediaType, blank=True, null=True)
    specification = models.TextField(_("Specification"), blank=True, null=True)
    tracklist = models.TextField(_("Tracklist"), blank=True, null=True)
    origPrice = models.DecimalField(_("Original price"),max_digits=7, decimal_places=2, blank=True, default=0.0)
    barcode = models.CharField(max_length=32, db_index=True, blank=True, null=True)
    pictureSource = models.TextField(_("Picture source"), blank=True, null=True)
    picture = models.ForeignKey(Picture, blank=True, null=True)
    slug = models.SlugField(max_length=126,blank=True,null=True) # will be created aftersave
    eshop = models.BooleanField(_("For E-Shop?"), 
                                help_text=_("Has items for sale in an eshop?"), 
                                default=False)
    to_store = models.DateTimeField(_("To store date of an item"), auto_now=True)
    discount = models.BooleanField(_("Has discount?"), 
                                   help_text=_("Has discount?"), 
                                   default=False)
    
    #history = HistoricalRecords()

    objects = models.Manager()
    objectsForEShop = ForEShopManager()
    objectsAtAction = AtActionManager()

    def hasItemsForShop(self):
        return self.item_set.all().filter(state__in = (Item.state_at_stock, Item.state_for_sale)).exists()
    
    @classmethod
    def updateEShop(cls):
        cursor = connection.cursor()
        cursor.execute("update store_article set eshop=True where id in (select distinct article_id from store_item where state in (%s,%s))",[Item.state_at_stock, Item.state_for_sale])
        cursor.execute("update store_article set eshop=False where id not in (select distinct article_id from store_item where state in (%s,%s))",[Item.state_at_stock, Item.state_for_sale])

    @classmethod
    def updateDiscount(cls):
        cursor = connection.cursor()
        cursor.execute("update store_article set discount=True where id in (select distinct article_id from store_item where id in (select distinct item_id from eshop_tradeaction))")
        cursor.execute("update store_article set discount=False where id not in (select distinct article_id from store_item where id in (select distinct item_id from eshop_tradeaction))")

            
    def _createSlug(self):
        title = self.title or 'unknown'
        interpret = self.interpret or 'unknown'
        year = self.year or 'someyear'
        slug = slugify(" ".join([aa for aa in (self.title,) if aa]))
        count = 1
        newslug = slug
        while Article.objects.filter(slug=newslug).count():
            newslug = slug + "-%02d" % (count,)
            count += 1
        self.slug=newslug

    def save(self,*args, **kwargs):
        self.slug = self._createSlug()
        super(Article,self).save(*args,**kwargs)

    def __unicode__(self):
        return u"%s (%s)" % (self.title, self.interpret)

    def _last_sold(self):
        return [0.0, None] # cena a datum

    def _for_sale_price_range(self):
        prices = [ ii['price'] for ii in self.item_set.filter(state__in=[Item.state_for_sale,Item.state_at_stock]).values('price')] or [0]
        return (min(prices), max(prices))

    lastSold = property(_last_sold)
    forSalePriceRange = property(_for_sale_price_range)


# class ItemState(models.Model):
#     name = models.CharField(_('Name'),max_length=40, unique=True)
#     desc = models.CharField(_("Description"), max_length=48, blank=True)
#     start = models.BooleanField(_("Start state"), unique=False)

#     @staticmethod
#     def getStart():
#         start = ItemState.objects.filter(start=True)
#         return start.count() and start[0]

#     def __unicode__(self):
#         return u"%s (%s)" % (self.desc, self.name)

# ItemState.state_at_stock = ItemState.objects.get(name='At stock')
# ItemState.state_cleaning = ItemState.objects.get(name='Cleaning')
# ItemState.state_for_sale = ItemState.objects.get(name='For sale')
# ItemState.state_sold = ItemState.objects.get(name='Sold')
# ItemState.state_ordered = ItemState.objects.get(name='Ordered')
# ItemState.state_expedited = ItemState.objects.get(name='Expedited')
    
# models.ForeignKey(ItemState, blank=True, null=True)

#     DATATYPES = ( (1,'basket number'),
#                   (2,'by store'),
#                   (3,'by eshop'),
#                   )

class Item(models.Model):
    STATES = ( (1,'At stock'),
               (2,'Cleaning'),
               (3,'For sale'),
               (4,'Ordered'),
               (5,'Expedited'),
               (6,'Sold'),
               )
    
    article = models.ForeignKey(Article)
    commentary = models.CharField(_('Commentary'), max_length=128, blank=True)
    barcode = models.CharField(_('Barcode'), max_length=128, blank=True, db_index=True)
    packnumber = models.CharField(_('Pack number'), max_length=128, blank=True,db_index=True)
    price = models.DecimalField(_('Price'), max_digits=7,decimal_places=2, blank=True, default=0.0)
    state = models.PositiveSmallIntegerField(_("State"), choices=STATES, default=1)
    last_modified = models.DateTimeField(_("Last modified"), auto_now=True)
    to_store = models.DateTimeField(_("To store date"), auto_now=True)
    home_page = models.BooleanField(_("Show at home page"), default=False)

    #history = HistoricalRecords()
    
    # def changeState(self,previous_state=None,target_state=None,**kwargs):
    #     ItemAction( item=self, action=ItemAction.STATES['change state'],  **kwargs).save()
    #     self.state = target_state

    # def save(self,*args, **kwargs):
    #     self.state = (self.state is not None and self.state) or Item.state_at_stock
    #     # if self.id:
    #     #     oldState = Item.objects.get(id=self.id).state
    #     #     if self.state != oldState:
    #     #         self.changeState(previous_state=oldState, target_state=self.state)
    #     #     super(Item,self).save(*args,**kwargs)
    #     # else:
    #     #     super(Item,self).save(*args,**kwargs)
    #     #     ItemAction(item=self, action=ItemAction.STATES['init state']).save()
    #     super(Item,self).save(*args,**kwargs)

    def has_tradeaction(self):
        return bool(len(self.tradeaction_set.all()))

    def __unicode__(self):
        result = u"/".join([ii for ii in [ unicode(self.article),unicode(self.barcode)] if ii]) \
                 + " | " \
                 + unicode(self.price) + u" Kč"
        return result

    class Meta:
        verbose_name = _('Item')
        verbose_name_plural = _('Items')
        
    @property
    def state_name(self):
        state = [s for s in Item.STATES if s[0] == self.state] or [(0,'unknown state'),]
        return state[0][1]

for state in Item.STATES:
    name = "state_" + state[1].lower().replace(" ","_")
    number = state[0]
    setattr(Item,name,number)
           
# class ItemAction(models.Model):
#     STATES = { "init state": 1,
#                "change state": 2 }

#     ACTIONS = ( (1, "init state"),
#                 (2, "change state") )
                
#     DATATYPES = ( (1,'basket number'),
#                   (2,'by store'),
#                   (3,'by eshop'),
#                   )
    
#     item = models.ForeignKey(Item)
#     action = models.PositiveSmallIntegerField(choices = ACTIONS)

#     type1 = models.PositiveSmallIntegerField(choices = DATATYPES, blank=True, null=True)
#     data1 = models.CharField(max_length=40, blank=True, null=True)

#     type2 = models.PositiveSmallIntegerField(choices = DATATYPES, blank=True, null=True)
#     data2 = models.CharField(max_length=40, blank=True, null=True)

#     type3 = models.PositiveSmallIntegerField(choices = DATATYPES, blank=True, null=True)
#     data3 = models.CharField(max_length=40, blank=True, null=True)

#     last_modified = models.DateTimeField(_("Last modified"), auto_now=True)
    

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
        results = Item.objects.filter(id__in=basket, state__in=(Item.state_for_sale,Item.state_at_stock))
        self.items = results
        self.total = len(self.items)
        self.total_price = calculateTotalPrice(self.items)
        return 

    def addItem(self,item):
        results = Item.objects.filter(id__in=[item.id,] + [ii.id for ii in self.items], state__in=(Item.state_for_sale,Item.state_at_stock))
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
            sold = Item.state_sold
            expedited = Item.state_expedited

            results = [ii for ii in self.items if ii.state in [Item.state_for_sale,Item.state_at_stock]]
            for item in results:
                item.state = sold
                item.save()
                item.state = expedited
                item.save()
            return
                
class ItemAction(TimeStampedModel):
    item = models.ForeignKey(Item)
    
