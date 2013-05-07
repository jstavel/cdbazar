# Create your views here.
from django.views.generic import TemplateView, ListView, DetailView, UpdateView, CreateView, FormView
from django.db.models import Q
from django import forms
from cdbazar.views import JSONTemplateResponse, prepare_render_to_response
from cdbazar.store.models import Article, Picture, Item, Basket, MediaType
from django.forms.models import modelformset_factory

from .forms import UserForm, OrderForm

class ArticleList(ListView,JSONTemplateResponse):
    model=Article
    paginate_by = 30

    page_includes = ['paginator.html','eshop/article_list/list.html','eshop/article_list/js.js']

    def get_template_names(self):
        return ['eshop/article_list.html',]

    def get_queryset(self):
        qs = super(ArticleList,self).get_queryset().filter(eshop=True)
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
        return context

    render_to_response = prepare_render_to_response(JSONTemplateResponse, ListView)

class ChooseItemForm(forms.Form):
    item = forms.IntegerField(widget = forms.Select())
    
    
class ToBasketView(DetailView, JSONTemplateResponse):
    model = Article
    template_name = "eshop/to_basket.html"
    
    page_includes = ['eshop/basket/summary.html','eshop/to_basket/done.html', 'eshop/to_basket/js.js', 'eshop/basket/js.js']
    
    def get_context_data(self,**kwargs):
        context = super(DetailView,self).get_context_data(**kwargs)
        basket = Basket(self.request)
        context['items_to_basket'] = context['article'].item_set.filter(state=Item.state_for_sale)

        self.more_items = False
        self.form = None
        if len(context['items_to_basket']) == 1:
            basket.addItem(context['items_to_basket'][0])
        else:
            self.more_items = True
            self.form = ChooseItemForm()

        context['basket'] = basket
        context['mediatypes'] = MediaType.objects.all()
        return context

    def get_template_names(self):
        return [ (not self.more_items and self.template_name) or "eshop/to_basket_choose.html" ]

    render_to_response = prepare_render_to_response(JSONTemplateResponse, DetailView)

class FromBasketView(DetailView, JSONTemplateResponse):
    model = Item
    template_name = "eshop/to_basket.html"
    
    page_includes = ['eshop/basket/summary.html','eshop/to_basket/done.html', 'eshop/to_basket/js.js', 'eshop/basket/js.js', 'eshop/basket_review/list.html', 'eshop/basket_review/js.js']
    
    def get_context_data(self,**kwargs):
        context = super(DetailView,self).get_context_data(**kwargs)
        basket = Basket(self.request)
        basket.removeItem(context['item'])
        context['basket'] = basket
        context['mediatypes'] = MediaType.objects.all()
        return context
    
    render_to_response = prepare_render_to_response(JSONTemplateResponse, DetailView)

class BasketView(TemplateView):
    model = Item
    template_name = "eshop/basket_review.html"
    
    page_includes = ['eshop/basket_review/review.html','eshop/basket_review/js.js']

    def get_context_data(self,**kwargs):
        context = TemplateView.get_context_data(self,**kwargs)
        basket = Basket(self.request)
        context['basket'] = basket
        context['mediatypes'] = MediaType.objects.all()
        context['orderform'] = getattr(self,'orderform',OrderForm())
        context['userform'] = getattr(self,'userform',UserForm())
        return context

    def post(self, request, *args, **kwargs):
        self.orderform = OrderForm(request.POST)
        self.userform = UserForm(request.POST)
        self.orderform.is_valid()
        self.userform.is_valid()
        return super(BasketView).post(self, request, *args, **kwargs)

class BuyView(TemplateView, JSONTemplateResponse):
    model = Item
    template_name = "eshop/buy.html"

    page_includes = ['eshop/basket_review/review.html','eshop/basket_review/js.js']
    
    def get_context_data(self,**kwargs):
        context = TemplateView.get_context_data(self,**kwargs)
        basket = Basket(self.request)
        basket.sell()
        basket._update()
        context['basket'] = basket
        context['mediatypes'] = MediaType.objects.all()
        return context

    
