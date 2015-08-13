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
    
class ArticleDetailView(DetailView,JSONTemplateResponse):
    model = Article
    page_includes = ['store/article_detail/detail.html',]
    render_to_response = prepare_render_to_response(JSONTemplateResponse, DetailView)

class ArticleList(ListView,JSONTemplateResponse):
    model=Article
    paginate_by = 30

    page_includes = ['paginator.html','store/article_list/list.html','store/article_list/js.js']

    def get_queryset(self):
        qs = super(ArticleList,self).get_queryset().order_by('-last_modified')
        search = self.request.GET.get('search',None)
        if search:
            qs = qs.filter(Q(title__icontains=search) | Q(interpret__icontains=search) | Q(barcode=search))
        mediaType__name = self.request.GET.get('mediaType',None)
        if mediaType__name:
            qs = qs.filter(mediaType__name = mediaType__name)
        return qs.select_related()

    def get_context_data(self,**kwargs):
        context = super(ArticleList,self).get_context_data(**kwargs)
        basket = Basket(self.request)
        context['basket'] = basket
        context['mediatypes'] = MediaType.objects.all().order_by('order')
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

class ItemList(ListView, JSONTemplateResponse):
    model=Item
    paginate_by = 50

    page_includes = ['paginator.html',
                     'store/item_list/list.html',
                     'store/item_list/js.js',
                     'store/basket_review/list.html',
                     'store/basket_review/js.js',
                     ]

    def get_queryset(self):
        qs = super(ItemList,self).get_queryset()
        qs = qs.filter(state__in=(Item.state_for_sale,Item.state_at_stock))

        search = self.request.GET.get('search',None)
        article_id = self.request.GET.get('article_id',None)
        mediaType__name = self.request.GET.get('mediaType',None)

        if article_id:
            qs = qs.filter(article__id = article_id)
        if search:
            qs = qs.filter(Q(article__title__icontains=search) | Q(article__interpret__icontains=search) | Q(barcode=search) | Q(packnumber=search))
        if mediaType__name:
            qs = qs.filter(article__mediaType__name = mediaType__name)

        order_by = self.get_order_by()
        order_desc = self.get_order_desc()
        return qs.order_by((order_desc=='asc' and "-" or "") + order_by).select_related()

    render_to_response = prepare_render_to_response(JSONTemplateResponse, ListView)
    
    def get_context_data(self,**kwargs):
        context = super(ItemList,self).get_context_data(**kwargs)
        context['basket'] = Basket(self.request)
        context['mediatypes'] = MediaType.objects.all().order_by('order')
        context['mediatype'] = self.request.GET.get('mediaType',None)
        context['pagestate_form'] = getattr(self,'pagestate_form', ItemListPageState(
            initial={'sort_by':'to_store','sort_order':'desc'}))
        return context

    def get_order_by(self):
        pagestate = getattr(self,'pagestate_form',None)
        if pagestate and pagestate.is_valid():
            return pagestate.cleaned_data['sort_by'] or "to_store"
        return "to_store"

    def get_order_desc(self):
        pagestate = getattr(self,'pagestate_form',None)
        if pagestate and pagestate.is_valid():
            return pagestate.cleaned_data['sort_order'] or "desc"
        return "asc"

    def get_page(self):
        pagestate = getattr(self,'pagestate_form',None)
        if pagestate and pagestate.is_valid():
            return pagestate.cleaned_data['page']
        return self.request.GET.get('page',1)

    def post(self, request, *args, **kwargs):
        self.pagestate_form = ItemListPageState(request.POST)
        self.kwargs['page'] = self.get_page()
        self.object_list = self.get_queryset()
        kwargs.update({'object_list': self.object_list})
        return self.render_to_response(self.get_context_data(**kwargs))

    render_to_response = prepare_render_to_response(JSONTemplateResponse, ListView)

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
    
    page_includes = ['store/basket/summary.html',
                     'store/to_basket/done.html',
                     'store/to_basket/js.js',
                     'store/basket/js.js',
                     'store/basket_review/list.html',
                     'store/basket_review/js.js',
                     ]
    
    def get_context_data(self,**kwargs):
        context = super(DetailView,self).get_context_data(**kwargs)
        basket = Basket(self.request)
        basket.addItem(context['item'])
        context['basket'] = basket
        context['mediatypes'] = MediaType.objects.all().order_by('order')
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
        context['mediatypes'] = MediaType.objects.all().order_by('order')
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
        context['items'] = self.form.is_bound and Item.objects.filter(barcode=self.form.cleaned_data['barcode'])\
                           .filter(state__in=(Item.state_for_sale,Item.state_at_stock))
        context['sold_items'] = self.form.is_bound and Item.objects.filter(barcode=self.form.cleaned_data['barcode'])\
                                .filter(state__in=(Item.state_expedited,Item.state_sold))
        return context

    def post(self,request,*args,**kwargs):
        self.form = BuyoutFormFactory(request.POST)
        self.form.is_valid()
        return TemplateView.get(self,request,*args,**kwargs)

    def get(self,request,*args,**kwargs):
        self.form = BuyoutFormFactory()
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
        context['article_form'] = self.article_form
        context['item_form'] = self.item_form
        context['barcode'] = self.barcode
        context['items'] = self.barcode and Item.objects.filter(barcode=self.barcode)
        if context['form']:
            context['form'].legend=""
        return context

    def post(self,request,*args,**kwargs):
        self.form = BuyoutFormFactory(request.POST)
        self.form2 = None
        self.form2_message = None
        self.article_form = ArticleForm(request.POST)
        self.item_form = ItemForm(request.POST)
        self.barcode = None
        
        if request.POST.get('form-ok',None):
            if self.form.is_valid():
                self.barcode = self.form.cleaned_data['barcode']
                barcode = self.barcode
                articles = Article.objects.filter(Q(title__icontains=barcode) | Q(interpret__icontains=barcode) | Q(barcode=barcode))
                initial = dict( [('barcode', self.barcode),] \
                              + ((len(articles) == 1) and [('article_id',articles[0].id)] or []))
                self.form2 = BuyoutToStockForm(initial=initial)  
                self.form2.fields['article_id'].choices=[(aa.id,str(aa)) for aa in articles]
                if len(articles) == 1:
                    self.form2.initial['article_id'] = articles[0].id
        if request.POST.get('form2-ok',None):
            self.form2 = BuyoutToStockForm(request.POST)
            barcode = request.POST.get('barcode',None)
            articles = Article.objects.filter(Q(title__icontains=barcode) | Q(interpret__icontains=barcode) | Q(barcode=barcode))
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
        self.article_form = ArticleForm()
        self.item_form = ItemForm()
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
        context['article_form'] = self.article_form
        context['item_form'] = self.item_form
        context['barcode'] = self.barcode
        context['items'] = self.barcode and Item.objects.filter(barcode=self.barcode)
        if context['form']:
            context['form'].legend=""
        return context

    def post(self,request,*args,**kwargs):
        print request.POST
        self.barcode = request.POST.get('buyout-barcode',None)
        self.form = BuyoutForm(request.POST.get('form-ok',None) and request.POST, initial={'barcode':self.barcode})
        self.form2 = None
        self.form2_message = None
        self.article_form = ArticleForm(request.POST.get('article-form-ok',None) and request.POST, initial={'barcode': self.barcode})
        self.item_form = ItemForm(request.POST.get('article-form-ok',None) and request.POST)
        
        if request.POST.get('form-ok',None):
            if self.form.is_valid():
                self.barcode = self.form.cleaned_data['barcode']
                barcode=self.barcode
                articles = Article.objects.filter(Q(title__icontains=barcode) | Q(interpret__icontains=barcode) | Q(barcode=barcode))
                initial = dict( [('barcode',barcode),] \
                                + ((len(articles) == 1) and [('article_id',articles[0].id)] or []))
                self.form2 = BuyoutToStoreForm( initial=initial )
                self.form2.fields['article_id'].choices=[(aa.id,str(aa)) for aa in articles]
                if len(articles) == 1:
                    self.form2.initial['article_id'] = articles[0].id

        if request.POST.get('form2-ok',None):
            self.form2 = BuyoutToStoreForm(request.POST)
            barcode = request.POST.get('choose-article-barcode',None)
            articles = Article.objects.filter(Q(title__icontains=barcode) | Q(interpret__icontains=barcode) | Q(barcode=barcode))
            self.form2.fields['article_id'].choices=[(aa.id,str(aa)) for aa in articles]
            if self.form2.is_valid():
                self.form2.save()
                self.form2 = None
                self.form2_message = "Hotovo, zbozi je na prodejne"

        if request.POST.get('article-form-ok',None):
            if self.article_form.is_valid() and self.item_form.is_valid():
                #barcode = request.POST.get('barcode',None)
                article = self.article_form.save()
                item = self.item_form.save(article=article, 
                                           state=Item.state_for_sale,
                                           barcode=article.barcode,
                )
                self.article_form = ArticleForm()
                self.item_form = ItemForm()
                self.form2_message = "Hotovo, zbozi je na prodejne"
            pass

        return TemplateView.get(self,request,*args,**kwargs)

    def get(self,request,*args,**kwargs):
        self.form = BuyoutForm()
        self.form2 = None
        self.form2_message = None
        self.barcode = None
        self.article_form = ArticleForm()
        self.item_form = ItemForm()
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
        self.form = BuyoutForm(request.POST)
        self.form2 = None
        self.form2_message = None
        self.barcode = None

        if request.POST.get('form-ok',None):
            if self.form.is_valid():
                self.barcode = self.form.cleaned_data['barcode']
                barcode = self.barcode
                articles = Article.objects.filter(Q(title__icontains=barcode) | Q(interpret__icontains=barcode) | Q(barcode=barcode))
                initial = dict( [('barcode',self.barcode),] \
                                + ((len(articles) == 1) and [('article_id',articles[0].id)] or []))
                self.form2 = BuyoutToCleanForm( initial = initial )
                self.form2.fields['article_id'].choices=[(aa.id,str(aa)) for aa in articles]
                if len(articles) == 1:
                    self.form2.initial['article_id'] = articles[0].id

            else:
                self.form = form
        if request.POST.get('form2-ok',None):
            self.form2 = BuyoutToCleanForm(request.POST)
            barcode = request.POST.get('barcode',None)
            articles = Article.objects.filter(Q(title__icontains=barcode) | Q(interpret__icontains=barcode) | Q(barcode=barcode))
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
                mediaType = MediaType.objects.all().filter(name=detail.type)
                articleData = dict(title = detail.title,
                                   interpret = detail.interpret,
                                   year = detail.year,
                                   publisher = detail.publisher,
                                   mediaType = mediaType and mediaType[0],
                                   specification = "", #detail.detail,
                                   tracklist = "", #detail.tracklists,
                                   origPrice = detail.price,
                                   barcode = detail.ean,
                                   pictureSource = detail.imgUrl,
                                   picture = Picture.loadFromURL(detail.imgUrl),
                               )
                if Article.objects.all().filter(barcode=detail.ean).count():
                    context['result'] = u"artikl s ean: %s už existuje. Přepisuji." % (detail.ean,)
                    for article in Article.objects.all().filter(barcode=detail.ean):
                        for key,value in articleData.items():
                            setattr(article,key,value)
                        pass
                else:
                    article = Article(**articleData)
                    article.save()
                    context['result'] = u"načteno"
            except:
                import traceback
                import sys
                traceback.print_exc(file=sys.stdout)
                #context['error'] = "chyba komunikace s audio3, %s" (sys.exc_info()[0],)
                context['error'] = "chyba komunikace s audio3"
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
        context['mediatypes'] = MediaType.objects.all().order_by('order')
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
        context['mediatypes'] = MediaType.objects.all().order_by('order')
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
    page_includes = ['store/item_field_update/form-header.html',
                     'store/item_field_update/form-body.html',
                     'store/item_field_update/js.js']
    template_name = 'store/item_field_update.html'

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
            form.success = True
            fieldName = form.fields.items()[0][0]
            form.value = getattr(form.instance,fieldName)

        return self.render_to_response(self.get_context_data(form=form))

    render_to_response = prepare_render_to_response(JSONTemplateResponse, TemplateView)


ArticlePictureLoadForm = forms.models.modelform_factory(Article, fields=['pictureSource'])

#  http://www.audio3.cz/goods.asp?stat=25&gid=1470770#
class ArticlePictureLoadView(TemplateView, JSONTemplateResponse):
    page_includes = ['store/article_load_picture/form-header.html',
                     'store/article_load_picture/form-body.html',
                     'store/article_load_picture/js.js']
    template_name = 'store/article_load_picture.html'

    def get(self, *args, **kwargs):
        article = Article.objects.get(pk=kwargs['pk'])
        return self.render_to_response(self.get_context_data(form=ArticlePictureLoadForm(instance=article)))

    def post(self, *args, **kwargs):
        article = Article.objects.get(pk=kwargs['pk'])
        form = ArticlePictureLoadForm(instance=article, data=self.request.POST)
        if form.is_valid():
            form.save()
            form.success = True
            form.redirect_to = "/store/article/%d/" % (article.pk)
            form.instance.picture = Picture.loadFromURL(form.cleaned_data['pictureSource'])
            form.instance.save()

        return self.render_to_response(self.get_context_data(form=form))

    render_to_response = prepare_render_to_response(JSONTemplateResponse, TemplateView)
