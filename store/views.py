#-*- coding: utf-8 -*-
# Create your views here.
from django.views.generic import TemplateView, ListView, DetailView, UpdateView, CreateView, FormView
from django.db.models import Q
from cdbazar.views import JSONTemplateResponse, prepare_render_to_response
from .forms import *
from .models import Article, Picture, Item, Basket, MediaType
from django.forms.models import modelformset_factory
import cdbazar.audio3
import sys, json
from django import http
from functools import partial
from cdbazar.eshop.models import TradeAction
import django.forms as forms

# def getArticles():
#     words = ["+" + ii for ii in re.split("[\ ]+",title)]
#     return articleManager.extra(tables=['summary_fulltext'],
#     			    where=['store_article.id=summary_fulltext.article_id',
#     				   'match (summary_fulltext.text) against (%s in boolean mode)'],
#     			    params=[" ".join(words)])
# try:
#     articles = (title and getArticles()) or (ean and articleManager.filter(ean=ean)) or []
# except:
#     errors.append(str(sys.exc_info()[1]))
#     pass
        
def prepare_get_form(superclass):
    def get_form(self,form_class):
        return superclass.get_form(self,form_class)

    return get_form

class MediaTypeCreateView(CreateView, JSONTemplateResponse):
    model = MediaType
    page_includes = ['store/mediatype_form/form.html',]
    render_to_response = prepare_render_to_response(JSONTemplateResponse, CreateView)
    
    def get_absolute_url(self):
        if 'success_url' in self.kwargs:
            return self.kwargs['success_url']
        return CreateView.get_absolute_url(self)

class ArticleCreateView(CreateView,JSONTemplateResponse):
    model = Article
    form_class = ArticleForm
    
    page_includes = ['store/article_form/form.html','store/article_form/js.js']
    render_to_response = prepare_render_to_response(JSONTemplateResponse, CreateView)

class ArticleUpdateView(UpdateView,JSONTemplateResponse):
    model = Article
    form_class = ArticleForm

    page_includes = ['store/article_form/form.html','store/article_form/js.js']
    render_to_response = prepare_render_to_response(JSONTemplateResponse, CreateView)
    
class ArticleList(ListView,JSONTemplateResponse):
    model=Article
    paginate_by = 30

    page_includes = ['paginator.html','store/article_list/list.html','store/article_list/js.js']

    def get_queryset(self):
        qs = super(ArticleList,self).get_queryset()
        search = self.request.GET.get('search',None)
        if search:
            qs = qs.filter(Q(title__icontains=search) | Q(interpret__icontains=search))
        mediaType__name = self.request.GET.get('mediaType',None)
        if mediaType__name:
            qs = qs.filter(mediaType__name = mediaType__name)
        return qs.select_related()

    def get_context_data(self,**kwargs):
        context = super(ArticleList,self).get_context_data(**kwargs)
        basket = Basket(self.request)
        context['basket'] = basket
        context['mediatypes'] = MediaType.objects.all()
        context['mediatype'] = self.request.GET.get('mediaType',None)
        context['tradeaction_banner_list'] = TradeAction.objects.all().order_by("?")[:20]
        context['new_articles_banner_list'] = Article.objects.all().order_by("to_store")[:20]
        return context

    render_to_response = prepare_render_to_response(JSONTemplateResponse, ListView)

class ItemUpdateView(UpdateView, JSONTemplateResponse):
    model = Item
    form_class = ItemForm
    
    page_includes = ['store/item_form/form_body.html', 'store/item_form/form_header.html', 'store/basket.html']

    def get_context_data(self,**kwargs):
        context = super(ItemUpdateView,self).get_context_data(**kwargs)
        article_form = ArticleItemForm(prefix='article', instance=self.object.article)
        context['article_form'] = article_form
        return context

    def form_valid(self,form):
        return UpdateView.form_valid(self,form)
    
    render_to_response = prepare_render_to_response(JSONTemplateResponse, UpdateView)

class ItemList(ListView,JSONTemplateResponse):
    model=Item
    paginate_by = 50

    page_includes = ['paginator.html','store/item_list/list.html','store/item_list/js.js']

    def get_queryset(self):
        qs = super(ItemList,self).get_queryset()
        qs = qs.filter(state__in=(Item.state_for_sale,Item.state_at_stock))

        search = self.request.GET.get('search',None)
        article_id = self.request.GET.get('article_id',None)
        mediaType__name = self.request.GET.get('mediaType',None)

        if article_id:
            qs = qs.filter(article__id = article_id)
        if search:
            qs = qs.filter(Q(article__title__icontains=search) | Q(article__interpret__icontains=search))
        if mediaType__name:
            qs = qs.filter(article__mediaType__name = mediaType__name)

        return qs.select_related()

    render_to_response = prepare_render_to_response(JSONTemplateResponse, ListView)
    
    def get_context_data(self,**kwargs):
        context = super(ItemList,self).get_context_data(**kwargs)
        context['basket'] = Basket(self.request)
        context['mediatypes'] = MediaType.objects.all()
        context['mediatype'] = self.request.GET.get('mediaType',None)
        return context

class ItemDataset(ListView):
    model=Item
    paginate_by = 50

    def get_queryset(self):
        qs = super(ItemDataset,self).get_queryset()
        qs = qs.filter(state__in=(Item.state_for_sale,Item.state_at_stock))

        search = self.request.GET.get('search',None)
        article_id = self.request.GET.get('article_id',None)
        mediaType__name = self.request.GET.get('mediaType',None)

        if article_id:
            qs = qs.filter(article__id = article_id)
        if search:
            qs = qs.filter(Q(article__title__icontains=search) | Q(article__interpret__icontains=search))
        if mediaType__name:
            qs = qs.filter(article__mediaType__name = mediaType__name)

        return qs.select_related()

    def render_to_response(self, context):
        content = [unicode(aa) + " | %s" % (aa.id,) for aa in context['object_list']]
        return http.HttpResponse(json.dumps(content), content_type='application/json')
    

class ToBasketView(DetailView, JSONTemplateResponse):
    model = Item
    template_name = "store/to_basket.html"
    
    page_includes = ['store/basket/summary.html','store/to_basket/done.html', 'store/to_basket/js.js', 'store/basket/js.js']
    
    def get_context_data(self,**kwargs):
        context = super(DetailView,self).get_context_data(**kwargs)
        basket = Basket(self.request)
        basket.addItem(context['item'])
        context['basket'] = basket
        context['mediatypes'] = MediaType.objects.all()
        return context

    render_to_response = prepare_render_to_response(JSONTemplateResponse, DetailView)

class FromBasketView(DetailView, JSONTemplateResponse):
    model = Item
    template_name = "store/to_basket.html"
    
    page_includes = ['store/basket/summary.html','store/to_basket/done.html', 'store/to_basket/js.js', 'store/basket/js.js', 'store/basket_review/list.html', 'store/basket_review/js.js']

    def get_context_data(self,**kwargs):
        context = super(DetailView,self).get_context_data(**kwargs)
        basket = Basket(self.request)
        basket.removeItem(context['item'])
        context['basket'] = basket
        context['mediatypes'] = MediaType.objects.all()
        return context

    render_to_response = prepare_render_to_response(JSONTemplateResponse, DetailView)

class BuyoutView(TemplateView):
    template_name = "store/buyout.html"
    page_includes = ['store/basket/summary.html', 'store/basket/js.js']

    def get_context_data(self,**kwargs):
        context = TemplateView.get_context_data(self,**kwargs)
        context['basket'] = Basket(self.request)
        context['form'] = self.form
        context['barcode'] = self.form.is_bound and self.form.cleaned_data['barcode']
        context['items'] = self.form.is_bound and Item.objects.filter(barcode=self.form.cleaned_data['barcode'])
        return context

    def post(self,request,*args,**kwargs):
        self.form = BuyoutForm(request.POST)
        self.form.is_valid()
        return TemplateView.get(self,request,*args,**kwargs)

    def get(self,request,*args,**kwargs):
        self.form = BuyoutForm()
        return TemplateView.get(self,request,*args,**kwargs)



# to stock:
# jen se ulozi - bez komentare, cisla obalky, cena jako last sold

# to store:
# cislo obalky - povinne, 
# cena - povinna, 
# komentar - nepovinny

# to clean:
# cislo obalky - nepovinne, 
# cena - povinna, 
# komentar - nepovinny

class BuyoutToStockView(TemplateView):
    template_name = "store/buyout.html"
    page_includes = ['store/basket/summary.html', 'store/basket/js.js']

    def get_context_data(self,**kwargs):
        context = TemplateView.get_context_data(self,**kwargs)
        context['title'] = u"Na sklad"
        context['basket'] = Basket(self.request)
        context['form'] = self.form
        context['form2'] = self.form2
        context['form2_message'] = self.form2_message
        context['barcode'] = self.barcode
        context['items'] = self.barcode and Item.objects.filter(barcode=self.barcode)
        if context['form']:
            context['form'].legend=""
        return context

    def post(self,request,*args,**kwargs):
        self.form = None
        self.form2 = None
        self.form2_message = None
        self.barcode = None

        if request.POST.get('form-ok',None):
            form = BuyoutForm(request.POST)
            if form.is_valid():
                self.barcode = form.cleaned_data['barcode']
                articles = Article.objects.filter(barcode=self.barcode)
                self.form2 = BuyoutToStockForm( initial={'barcode':self.barcode} )
                self.form2.fields['article_id'].choices=[(aa.id,str(aa)) for aa in articles]
            else:
                self.form = form
        if request.POST.get('form2-ok',None):
            self.form2 = BuyoutToStockForm(request.POST)
            barcode = request.POST.get('barcode',None)
            articles = Article.objects.filter(barcode=barcode)
            self.form2.fields['article_id'].choices=[(aa.id,str(aa)) for aa in articles]
            if self.form2.is_valid():
                self.form2.save()
                self.form2 = None
                self.form2_message = "Hotovo, zbozi je na sklade"
                self.form = BuyoutForm()

        return TemplateView.get(self,request,*args,**kwargs)

    def get(self,request,*args,**kwargs):
        self.form = BuyoutForm()
        self.form2 = None
        self.form2_message = None
        self.barcode = None
        return TemplateView.get(self,request,*args,**kwargs)

class BuyoutToStoreView(TemplateView):
    template_name = "store/buyout.html"
    page_includes = ['store/basket/summary.html', 'store/basket/js.js']

    def get_context_data(self,**kwargs):
        context = TemplateView.get_context_data(self,**kwargs)
        context['title'] = u"Na prodejnu"
        context['basket'] = Basket(self.request)
        context['form'] = self.form
        context['form2'] = self.form2
        context['form2_message'] = self.form2_message
        context['barcode'] = self.barcode
        context['items'] = self.barcode and Item.objects.filter(barcode=self.barcode)
        if context['form']:
            context['form'].legend=""
        return context

    def post(self,request,*args,**kwargs):
        self.form = None
        self.form2 = None
        self.form2_message = None
        self.barcode = None

        if request.POST.get('form-ok',None):
            form = BuyoutForm(request.POST)
            if form.is_valid():
                self.barcode = form.cleaned_data['barcode']
                articles = Article.objects.filter(barcode=self.barcode)
                self.form2 = BuyoutToStoreForm( initial={'barcode':self.barcode} )
                self.form2.fields['article_id'].choices=[(aa.id,str(aa)) for aa in articles]
            else:
                self.form = form
        if request.POST.get('form2-ok',None):
            self.form2 = BuyoutToStoreForm(request.POST)
            barcode = request.POST.get('barcode',None)
            articles = Article.objects.filter(barcode=barcode)
            self.form2.fields['article_id'].choices=[(aa.id,str(aa)) for aa in articles]
            if self.form2.is_valid():
                self.form2.save()
                self.form2 = None
                self.form2_message = "Hotovo, zbozi je na sklade"
                self.form = BuyoutForm()

        return TemplateView.get(self,request,*args,**kwargs)

    def get(self,request,*args,**kwargs):
        self.form = BuyoutForm()
        self.form2 = None
        self.form2_message = None
        self.barcode = None
        return TemplateView.get(self,request,*args,**kwargs)

class BuyoutToCleanView(TemplateView):
    template_name = "store/buyout.html"
    page_includes = ['store/basket/summary.html', 'store/basket/js.js']

    def get_context_data(self,**kwargs):
        context = TemplateView.get_context_data(self,**kwargs)
        context['title'] = u"K čištění"
        context['basket'] = Basket(self.request)
        context['form'] = self.form
        context['form2'] = self.form2
        context['form2_message'] = self.form2_message
        context['barcode'] = self.barcode
        context['items'] = self.barcode and Item.objects.filter(barcode=self.barcode)
        if context['form']:
            context['form'].legend=""
        return context

    def post(self,request,*args,**kwargs):
        self.form = None
        self.form2 = None
        self.form2_message = None
        self.barcode = None

        if request.POST.get('form-ok',None):
            form = BuyoutForm(request.POST)
            if form.is_valid():
                self.barcode = form.cleaned_data['barcode']
                articles = Article.objects.filter(barcode=self.barcode)
                self.form2 = BuyoutToCleanForm( initial={'barcode':self.barcode} )
                self.form2.fields['article_id'].choices=[(aa.id,str(aa)) for aa in articles]
            else:
                self.form = form
        if request.POST.get('form2-ok',None):
            self.form2 = BuyoutToCleanForm(request.POST)
            barcode = request.POST.get('barcode',None)
            articles = Article.objects.filter(barcode=barcode)
            self.form2.fields['article_id'].choices=[(aa.id,str(aa)) for aa in articles]
            if self.form2.is_valid():
                self.form2.save()
                self.form2 = None
                self.form2_message = "Hotovo, zbozi je na sklade"
                self.form = BuyoutForm()

        return TemplateView.get(self,request,*args,**kwargs)

    def get(self,request,*args,**kwargs):
        self.form = BuyoutForm()
        self.form2 = None
        self.form2_message = None
        self.barcode = None
        return TemplateView.get(self,request,*args,**kwargs)

class BuyoutLookupView(TemplateView,JSONTemplateResponse):
    template_name = "store/buyout/lookup.html"
    page_includes = ['store/buyout/lookup.html','store/js.js']

    def get_context_data(self,**kwargs):
        context = TemplateView.get_context_data(self,**kwargs)
        barcode = self.request.GET.get('barcode',None)
        try:
            context['results'] = barcode and cdbazar.audio3.search(ean=barcode)[0]
        except IOError:
            context['error'] = "chyba komunikace s audio3"
        return context

    render_to_response = prepare_render_to_response(JSONTemplateResponse, TemplateView)

class BuyoutLoadDetailView(TemplateView,JSONTemplateResponse):
    template_name = "store/buyout/load_detail.html"
    page_includes = ['store/buyout/load_detail.html','store/buyout/js.js']

    def get_context_data(self,**kwargs):
        context = TemplateView.get_context_data(self,**kwargs)
        gid = self.request.GET.get('gid',None)
        if gid:
            try:
                detail = cdbazar.audio3.Detail(gid)
                if Article.objects.all().filter(barcode=detail.ean).count():
                    context['result'] = u"artikl s ean: %s už existuje. Přeskakuji." % (detail.ean,)
                else:
                    mediaType = MediaType.objects.all().filter(name=detail.type)
                    article = Article(title = detail.title,
                                      interpret = detail.interpret,
                                      year = detail.year,
                                      publisher = detail.publisher,
                                      mediaType = mediaType and mediaType[0],
                                      specification = detail.detail,
                                      tracklist = detail.tracklists,
                                      origPrice = detail.price,
                                      barcode = detail.ean,
                                      pictureSource = "<img src='%s'>picture</img>" % (detail.imgUrl,),
                                      )
                    article.save()
                    context['result'] = u"načteno"
            except:
                context['error'] = "chyba komunikace s audio3, %s" (sys.exc_info()[0],)
        return context

    render_to_response = prepare_render_to_response(JSONTemplateResponse, TemplateView)

# 0652637291629
class BasketView(TemplateView, JSONTemplateResponse):
    model = Item
    template_name = "store/basket_review.html"
    
    page_includes = ['store/basket_review/list.html','store/basket_review/js.js']
    
    def get_context_data(self,**kwargs):
        context = TemplateView.get_context_data(self,**kwargs)
        basket = Basket(self.request)
        context['basket'] = basket
        context['mediatypes'] = MediaType.objects.all()
        return context

    render_to_response = prepare_render_to_response(JSONTemplateResponse, TemplateView)


class SellView(TemplateView):
    model = Item
    template_name = "store/sell.html"
    
    def get_context_data(self,**kwargs):
        context = TemplateView.get_context_data(self,**kwargs)
        basket = Basket(self.request)
        basket.sell()
        basket._update()
        context['basket'] = basket
        context['mediatypes'] = MediaType.objects.all()
        return context

ArticleFormFactory = partial(forms.models.modelform_factory, Article)
ItemFormFactory = partial(forms.models.modelform_factory, Item)

ArticleFieldForms = dict(
    [ (field,ArticleFormFactory(fields=[field,])) for field in ('interpret','title','year',
                                                                'mediaType',
                                                            ) ]
)

ItemFieldForms = dict(
    [ (field, ItemFormFactory(fields=[field,])) for field in ('barcode',
                                                              'packnumber',
                                                              'home_page',
                                                              'commentary', 
                                                              'price') ]
)

class ItemFieldUpdateView(TemplateView, JSONTemplateResponse):
    page_includes = ['store/item_field_update/form.html','store/item_field_update/js.js']
    template_name = 'store/item_field_update.html'
    success_template_name = 'store/item_field/success.html'

    def get(self, *args, **kwargs):
        field = kwargs['field']
        item = Item.objects.get(pk=kwargs['pk'])
        object = field in ItemFieldForms and item or item.article
        form_class = ItemFieldForms.get(field) or ArticleFieldForms.get(field)
        return self.render_to_response(self.get_context_data(form=form_class(instance=object)))

    def post(self, *args, **kwargs):
        field = kwargs['field']
        item = Item.objects.get(pk=kwargs['pk'])
        object = field in ItemFieldForms and item or item.article
        form_class = ItemFieldForms.get(field) or ArticleFieldForms.get(field)
        form = form_class(instance=object, data=self.request.POST)
        if form.is_valid():
            form.save()

        return self.render_to_response(self.get_context_data(form=form))

    render_to_response = prepare_render_to_response(JSONTemplateResponse, TemplateView)
