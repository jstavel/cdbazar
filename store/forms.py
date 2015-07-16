# -*- coding: utf-8 -*-
from .models import Article, Picture, Item
from django.utils.translation import ugettext as _

import django.forms as forms

SORTS = (('to_store',u"Od nejnovějšího"),
         ('article__mediaType',u"Typ media"),
         ('article__interpret',u"Interpret"),
         ('article__title',u"Titul"),
         ('article__year',u"Rok"),
         ('barcode',u"EAN"),
         ('packnumber',u"EAN"))

class ItemListPageState(forms.Form):
    sort_by = forms.ChoiceField(choices = SORTS, required=False, widget=forms.HiddenInput)
    page = forms.IntegerField( required=False, widget=forms.HiddenInput )
    query = forms.CharField(max_length=128, required=False, widget=forms.HiddenInput)
    

class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        exclude = ('picture',)

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        exclude = ('article',)
        
class ArticleItemForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ('title','interpret','year','mediaType')
        
class BuyoutForm(forms.Form):
    legend = u"Výkup"
    barcode = forms.CharField(max_length=120)


CHOICES = (('1', 'First',), ('2', 'Second',))

# to stock:
# jen se ulozi - bez komentare, cisla obalky, cena jako last sold
#
# to stock
# naskladnuje se jen to, co uz tady jednou bylo.
# prebira se cena, nic se nezadava.
#

class BuyoutToStockForm(forms.Form):
    legend = u"Vyberte zboží na sklad"
    barcode = forms.CharField(max_length=120, widget=forms.HiddenInput)
    article_id = forms.ChoiceField(label=u"Zboží", widget=forms.RadioSelect, choices = CHOICES)
    
    def save(self):
        article = Article.objects.get(id=self.cleaned_data['article_id'])
        article.eshop=True
        item = article.item_set.create(price = article.lastSold[0], barcode=article.barcode, state = Item.state_at_stock)
        article.save()
        
# to store:
# cislo obalky - povinne, 
# cena - povinna, 
# komentar - nepovinny

class BuyoutToStoreForm(forms.Form):
    legend = _("Choose an item to store")
    barcode = forms.CharField(max_length=120, widget=forms.HiddenInput)
    article_id = forms.ChoiceField(label=_("Goods"), widget=forms.RadioSelect, choices = CHOICES)
    packnumber = forms.CharField(label=_("Packnumber"), max_length=32)
    price = forms.FloatField(label=_("Price"))
    commentary = forms.CharField(label=_("Commentary"), max_length=48, required=False)
    
    def clean(self):
        article = Article.objects.get(id=self.cleaned_data['article_id'])
        packnumber = self.cleaned_data.get('packnumber','')
        itemsInStore = Item.objects.filter(article__mediaType = article.mediaType, 
                                           packnumber = packnumber, 
                                           state__in=( Item.state_at_stock,
                                                       Item.state_cleaning,
                                                       Item.state_for_sale )
                                           )
        if packnumber.strip().isdigit() and len(itemsInStore) > 0:
            raise forms.ValidationError(unicode(_('Item with given packnumber is already used.')) + "&nbsp;".join(['<a href="/store/item/%s">%s</a>' % (aa.id,unicode(aa)) for aa in itemsInStore]))
        return self.cleaned_data
    
    def save(self):
        article = Article.objects.get(id=self.cleaned_data['article_id'])
        article.eshop=True
        item = article.item_set.create(price = self.cleaned_data['price'],
                                       packnumber = self.cleaned_data['packnumber'],
                                       barcode=article.barcode, 
                                       state = Item.state_for_sale,
                                       commentary=self.cleaned_data['commentary']
                                       )
        article.save()

# to clean:
# cislo obalky - nepovinne, 
# cena - povinna, 
# komentar - nepovinny

class BuyoutToCleanForm(forms.Form):
    legend = _("Choose an item to clean")
    barcode = forms.CharField(max_length=120, widget=forms.HiddenInput)
    article_id = forms.ChoiceField(label=_("Goods"), widget=forms.RadioSelect, choices = CHOICES)
    packnumber = forms.CharField(label=_("Packnumber"), max_length=32, required=False)
    price = forms.FloatField(label=_("Price"))
    commentary = forms.CharField(label=_("Commentary"), max_length=48, required=False)

    def clean(self):
        article = Article.objects.get(id=self.cleaned_data['article_id']) 
        packnumber = self.cleaned_data['packnumber']
        itemsInStore = Items.objects.filter(article__mediaType = article.mediaType, 
                                            packnumber = packnumber, 
                                            state__in=( Item.state_at_stock,
                                                        Item.state_at_cleaning,
                                                        Item.state_for_sale )
                                            )
        if packnumber.strip().isdigit() and len(itemsInStore) > 0:
            raise forms.ValidationError(unicode(_('Item with given packnumber is already used.')) + "&nbsp;".join(['<a href="/store/item/%s">%s</a>' % (aa.id,unicode(aa)) for aa in itemsInStore]))
        return self.cleaned_data

    def save(self):
        article = Article.objects.get(id=self.cleaned_data['article_id'])
        item = article.item_set.create(price = article.lastSold[0], barcode=barcode, state = Item.state_at_stock)

class ItemToCleanForm(forms.Form):
    article_id = forms.CharField(widget=forms.HiddenInput, required=True)
    barcode = forms.CharField(widget=forms.HiddenInput, required=False)
    packnumber = forms.CharField(label=_("Pack number"), required=False)
    price = forms.FloatField(label=_("Price"), required=True, initial=0.0)
    commentary = forms.CharField(label=_("Commentary"), required=False)

    """ zkontrolovat packnumber, ze neni v prodeji """
    def clean(self):
	article=Article.objects.get(id=self.cleaned_data['article_id'])
    	inStore = False
    	""" zkontrolovat, jestli neexistuje nejake zbozi, co nema stav sold
    	a stejne cislo obalky - jestli je cislo obalky ciselne """
    	items = Item.objects
    	packnumber = self.cleaned_data['packnumber']
    	itemsInStore = items.filter(article__articleType=article.articleType, packnumber=packnumber,state = Item.state_for_sale)
    	inStore = len(itemsInStore) > 0
    	if packnumber.strip().isdigit() and inStore:
    	    raise forms.ValidationError(unicode(_('Item with given packnumber is already in the store.')) + "&nbsp;".join(['<a href="/store/item/?q=%s">%s</a>' % (aa.barcode or aa.article.ean,unicode(aa)) for aa in itemsInStore]))
    	return self.cleaned_data

    def save(self):
        pass
#
# CHOICES = (('1', 'First',), ('2', 'Second',))
# >>> choice_field = forms.ChoiceField(widget=forms.RadioSelect, choices=CHOICES)
# >>> choice_field.choices
#
