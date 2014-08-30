#-*- coding:utf-8 -*-
# Create your views here.

from django.views.generic import (
    TemplateView, 
    ListView, 
    DetailView, 
    UpdateView, 
    CreateView, 
    FormView, 
    DeleteView,

)
from django.utils.translation import ugettext as _
from django.views.generic.detail import BaseDetailView
import json    
from django.db.models import Q
from django import forms
from cdbazar.views import JSONTemplateResponse, prepare_render_to_response
from cdbazar.store.models import Article, Picture, Item, MediaType
from django.forms.models import modelformset_factory
from django.shortcuts import render_to_response
from django.template import RequestContext, loader, Context
from decimal import Decimal, getcontext, ROUND_HALF_UP, localcontext
from itertools import chain
import re
from .forms import *
from .models import (
    Order, 
    additionalItem, 
    DeliveryPrice, 
    PaymentPrice, 
    TradeAction, 
    News, 
    Basket, 
    PAYMENT_WAYS, 
    DELIVERY_WAYS
)
from django.shortcuts import redirect
from django.forms.models import inlineformset_factory
from django.forms import widgets
from django.core.mail import send_mail
from django.http import HttpResponse
from django.contrib import messages
from django_xhtml2pdf.utils import render_to_pdf_response
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login,logout

class AddTradeActionView(TemplateView, JSONTemplateResponse):
    template_name = "eshop/tradeaction_add.html"
    page_includes = ['eshop/tradeaction_add/js.js', 'eshop/tradeaction_add/form.html']
    
    def get_context_data(self,**kwargs):
        if self.request.method == 'GET':
            self.success_url_form = SuccessURLForm(self.request.GET)
        else:
            self.success_url_form = SuccessURLForm()
        obj = getattr(self,'object',None)
        if not obj:
            self.object = Item.objects.get(pk=kwargs['pk'])

        context = super(AddTradeActionView,self).get_context_data(**kwargs)
        context['object'] = self.object
        form = getattr(self,'form',None)
        if not form:
            formset=inlineformset_factory(Item, TradeAction)
            context['form'] = formset(instance=self.object)
        else:
            context['form'] = form
        context['success_url_form'] = self.success_url_form
        return context

    def post(self, request, *args, **kwargs):
        self.success_url_form = SuccessURLForm(self.request.POST)
        
        obj = getattr(self,'object',None)
        if not obj:
            self.object = Item.objects.get(pk=kwargs['pk'])
            
        formset=inlineformset_factory(Item, TradeAction)
        form = formset(request.POST, request.FILES, instance=self.object)
        self.form = form
        if form.is_valid():
            form.save()
            if self.success_url_form.is_valid() and self.success_url_form.cleaned_data['success_url']:
                return redirect(self.success_url_form.cleaned_data['success_url'])
            pass
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

    render_to_response = prepare_render_to_response(JSONTemplateResponse, TemplateView)

class TradeActionDelete(DeleteView):
    success_url = "/eshop/tradeaction/"
    model = TradeAction

class TradeActionList(ListView,JSONTemplateResponse):
    model=TradeAction
    paginate_by = 50

    page_includes = ['paginator.html','eshop/tradeaction_list/list.html','eshop/tradeaction_list/js.js']

    def get_queryset(self):
        qs = super(TradeActionList,self).get_queryset()
        search = self.request.GET.get('search',None)
        if search:
            qs = qs.filter(Q(article__title__icontains=search) | Q(article__interpret__icontains=search))
        mediaType__name = self.request.GET.get('mediaType',None)
        if mediaType__name:
            qs = qs.filter(mediaType__name = mediaType__name)
        return qs.select_related()

    def get_context_data(self,**kwargs):
        context = super(TradeActionList,self).get_context_data(**kwargs)
        basket = Basket(self.request)
        context['basket'] = basket
        context['mediatypes'] = MediaType.objects.all()
        context['mediatype'] = self.request.GET.get('mediaType',None)
        return context

    render_to_response = prepare_render_to_response(JSONTemplateResponse, ListView)

class OrderList(ListView,JSONTemplateResponse):
    model=Order
    paginate_by = 50

    page_includes = ['paginator.html',
                     'eshop/order_list/form.html', 
                     'eshop/order_list/list.html',
                     'eshop/order_list/js.js']

    def get_queryset(self):
        qs = super(OrderList,self).get_queryset()
        state = self.request.GET.get('state',None)
        if state:
            qs = qs.filter(state=state)
        return qs.order_by('-pk',).select_related()

    def get_context_data(self,**kwargs):
        context = super(OrderList,self).get_context_data(**kwargs)
        context['orderState'] = int(self.request.GET.get('state','0'))
        available_transitions = len(context['object_list']) and context['object_list'][0].available_transitions()
        context['form'] = getattr(self,'form',OrderTransitionForm())
        if available_transitions:
            context['form'].fields['transition'].choices = [(0,'--- vyber si ---'),] + \
                                                           map(lambda tr: (tr,_(tr)), available_transitions)
        return context

    def post(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        available_transitions = len(self.object_list) and self.object_list[0].available_transitions()
        self.form = OrderTransitionForm(request.POST)
        if available_transitions:
            self.form.fields['transition'].choices = [(0,'--- vyber si ---'),] + \
                                                     map(lambda tr: (tr,_(tr)), available_transitions)
        if request.POST.get('submit',"") == u"načíst šablonu":
            def valueFactory(value):
                def value_from_datadict(data, files, prefix):
                    return value
                return value_from_datadict
            try:
                emailMessage = EmailMessage.objects.get(id=request.POST.get('emailMessageID',0))
                self.form.fields['subject'].widget.value_from_datadict = valueFactory(emailMessage.title)
                self.form.fields['message'].widget.value_from_datadict = valueFactory(emailMessage.text)
            except EmailMessage.DoesNotExist:
                self.form.fields['subject'].widget.value_from_datadict = valueFactory("")
                self.form.fields['message'].widget.value_from_datadict = valueFactory("")
                pass
        else:
            if self.form.is_valid():
                context = self.get_context_data(object_list=self.object_list)
                data = self.form.cleaned_data
                if data['subject'] and data['transition']:
                    selectedOrderKeys = filter(lambda key: re.match('order-[0-9]+', key), request.POST.keys())
                    selectedOrderIDs = map(lambda key: int(key.split('-')[1]), selectedOrderKeys)
                    for order in filter(lambda order: order.id in selectedOrderIDs, context['object_list']):
                        sendTransitionEmail(data['subject'],
                                            data['message'],
                                            order.contact_email, 
                                            order)
                        order.processTransition(data['transition'])
                        order.save()
                        pass
                    messages.add_message(request, messages.INFO, 'Rozeslal jsem emaily.')
                    return redirect("/eshop/order")

        return super(OrderList,self).get(request, *args, **kwargs)

    render_to_response = prepare_render_to_response(JSONTemplateResponse, ListView)

class ArticleListState(forms.Form):
    active_banner = forms.CharField(label="active banner",
                                    initial = 'tradeaction',
                                    required = False,
                                    widget=forms.HiddenInput())
    active_articles_list = forms.CharField(label="active articles list", 
                                              initial="goods",
                                              widget=forms.HiddenInput())
    active_media = forms.CharField(label="selected media",
                                   initial = None,
                                   widget=forms.HiddenInput())
    

class ArticleList(ListView,JSONTemplateResponse):
    model=Article
    paginate_by = 30

    page_includes = ['paginator.html',
                     'eshop/article_list/list.html',
                     'eshop/article_list/list-by-cheaper.html',
                     'eshop/article_list/list_shortly.html',
                     'eshop/article_list/js.js',
                     'eshop/article_list/tradeaction_banner.html',
                     'eshop/article_list/tradeaction_banner.js',
                     'eshop/article_list/new_articles_banner.html',
                     'eshop/article_list/new_articles_banner.js',
                     ]

    def get_template_names(self):
        return ['eshop/article_list.html',]

    def get_queryset(self):
        qs = super(ArticleList,self).get_queryset().filter(eshop=True)
        search = self.request.GET.get('search',None)
        if search:
            qs = qs.filter(Q(title__icontains=search) | Q(interpret__icontains=search))
        mediaType__name = self.request.GET.get('mediaType',None)
        if mediaType__name and mediaType__name != 'all':
            qs = qs.filter(mediaType__name = mediaType__name)
        return qs.select_related()

    def get_queryset_for_new_articles(self):
        qs = Article.objects.all().filter(eshop=True).order_by('to_shop')
        search = self.request.GET.get('search',None)
        if search:
            qs = qs.filter(Q(title__icontains=search) | Q(interpret__icontains=search))
        mediaType__name = self.request.GET.get('mediaType',None)
        if mediaType__name:
            qs = qs.filter(mediaType__name = mediaType__name)
        return qs

    def get_queryset_for_articles_with_tradeaction(self):
        qs = Article.objects.all().filter(discount=True)
        search = self.request.GET.get('search',None)
        if search:
            qs = qs.filter(Q(title__icontains=search) | Q(interpret__icontains=search))
        mediaType__name = self.request.GET.get('mediaType',None)
        if mediaType__name:
            qs = qs.filter(mediaType__name = mediaType__name)
        return qs
        
    def get_context_data(self,**kwargs):
        context = super(ArticleList,self).get_context_data(**kwargs)
        basket = Basket(self.request)
        context['object_list_by_cheaper'] = context.get('object_list',[])
        context['articles_with_tradeaction'] = self.get_queryset_for_articles_with_tradeaction()
        context['news_list'] = News.objects.all().order_by('created')[:5]
        context['new_articles'] = self.get_queryset_for_new_articles()
        context['basket'] = basket
        context['mediatypes'] = MediaType.objects.all()
        context['mediatype'] = self.request.GET.get('mediaType',None)
        context['tradeaction_banner_list'] = TradeAction.objects.all().order_by("?")[:20]
        context['new_articles_banner_list'] = Article.objects.all().order_by("to_store")[:20]
        context['reservation_form'] = getattr(self,
                                              'reservation_form',
                                              ReservationForm(initial={'query':
                                                                       self.request.GET.get('search',"")
                                                                   }
                                                          ))
        print context['reservation_form'].is_bound
        return context

    def post(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        kwargs.update({'object_list': self.object_list})
        self.reservation_form = ReservationForm(request.POST)
        if self.reservation_form.is_valid():
            self.reservation_form.save()
        return self.render_to_response(self.get_context_data(**kwargs))

    render_to_response = prepare_render_to_response(JSONTemplateResponse, ListView)

class ChooseItemForm(forms.Form):
    item = forms.IntegerField(widget = forms.Select())

class ArticleDetail(DetailView, JSONTemplateResponse):
    model = Article
    template_name = "eshop/article_detail.html"
    page_includes = ['eshop/basket/summary.html',
                     'eshop/article_detail/detail.html', 
                     'eshop/article_detail/js.js', 
                     'eshop/basket/js.js']
    
    def get_template_names(self):
        return [self.template_name]

    def get_context_data(self,**kwargs):
        context = super(ArticleDetail,self).get_context_data(**kwargs)
        basket = Basket(self.request)
        context['basket'] = basket
        return context

    render_to_response = prepare_render_to_response(JSONTemplateResponse, DetailView)
    
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

        #if len(context['items_to_basket']) == 1:
        basket.addItem(context['items_to_basket'][0])
        #else:
        #    self.more_items = True
        #    self.form = ChooseItemForm()

        context['basket'] = basket
        context['mediatypes'] = MediaType.objects.all()
        return context

    def get_template_names(self):
        return [ (not self.more_items and self.template_name) or "eshop/to_basket_choose.html" ]

    render_to_response = prepare_render_to_response(JSONTemplateResponse, DetailView)

class FromBasketView(DetailView, JSONTemplateResponse):
    model = Item
    template_name = "eshop/from_basket.html"
    page_includes = ['eshop/basket/summary.html','eshop/from_basket/done.html', 'eshop/from_basket/js.js', 'eshop/basket/js.js', 'eshop/basket_review/review.html', 'eshop/basket_review/js.js']
    
    def get_context_data(self,**kwargs):
        context = super(DetailView,self).get_context_data(**kwargs)
        basket = Basket(self.request)
        basket.removeItem(context['item'])
        context['basket'] = basket
        context['mediatypes'] = MediaType.objects.all()
        return context
    
    render_to_response = prepare_render_to_response(JSONTemplateResponse, DetailView)

class BasketView(TemplateView,JSONTemplateResponse):
    model = Item
    template_name = "eshop/basket_review.html"
    page_includes = ['eshop/basket_review/review.html','eshop/basket_review/js.js']

    def get_context_data(self,**kwargs):
        context = TemplateView.get_context_data(self,**kwargs)
        context['basket'] = getattr(self,'basket',Basket(self.request))
        context['mediatypes'] = MediaType.objects.all()
        context['order_login_form'] = getattr(self,'order_login_form',AuthenticationForm())
        context['order_invoicing_form'] = getattr(self,'order_invoicing_form',OrderInvoicingForm())
        context['order_contact_form'] = getattr(self,'order_contact_form',  OrderContactForm())
        context['order_delivery_way_form'] = getattr(self,'order_delivery_way_form', OrderDeliveryWayForm())
        context['order_payment_way_form'] = getattr(self,'order_payment_way_form',  OrderPaymentWayForm())
        context['order_delivery_form'] = getattr(self,'order_delivery_form', OrderDeliveryForm())
        context['order_payment_form'] = getattr(self,'order_payment_form',  OrderPaymentForm())
        context['userform'] = getattr(self,'userform',UserForm())
        context['order_stage_form'] = getattr(self,'order_stage_form',OrderStageForm())
        return context
    
    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        basket = context['basket']

        # vycisteni basket od automatickych polozek, ktere zavisi na objednavce
        basket.removeAdditionalItem(toBeRemoved = lambda item: 'by-order' in item.type)

        delivery_way = context['order_delivery_way_form'].fields['delivery_way'].initial
        basket.addAdditionalItem(DeliveryPrice.asAdditionalItemForBasket(delivery_way))

        payment_way = context['order_payment_way_form'].fields['payment_way'].initial
        basket.addAdditionalItem(PaymentPrice.asAdditionalItemForBasket(payment_way))

        # jestli je uzivatel prihlasen a ma slevu, tak doplnime
        if request.user.is_authenticated() and request.user.getUserDiscount():
            price = (-1 * Decimal(basket.total_price) * \
                     Decimal("0.01") * \
                     Decimal(request.user.getUserDiscount())) \
                .quantize(Decimal('0'), rounding=ROUND_HALF_UP)
            basket.addAdditionalItem( request.user.getUserDiscountAsAdditionalItem(price) )
        return self.render_to_response(context)
            
    def post(self, request, *args, **kwargs):
        self.order_login_form = AuthenticationForm(data=request.POST)
        if 'login' in request.POST:
            if self.order_login_form.is_valid():
                user = self.order_login_form.get_user()
                login(request, user)
                # nacteni dat z minule objednavky a predvyplneni
                # default hodnot
                olderOrders = Order.objects.filter(user=user).order_by('id')
                olderOrder = olderOrders and olderOrders[0]
                if olderOrder:
                    print "naplneni daty z predeslych objednavek"
                    keys = [aa.name for aa in olderOrder._meta.fields]
                    initial = dict([(key,getattr(olderOrder,key)) for key in keys])
                    self.order_invoicing_form = OrderInvoicingForm(initial=initial)
                    self.order_contact_form = OrderContactForm(initial=initial)
                    self.order_delivery_form = OrderDeliveryForm(initial=initial)
                    self.order_payment_form = OrderPaymentForm(initial=initial)
                    self.order_delivery_way_form = OrderDeliveryWayForm(initial=initial)
                    self.order_payment_way_form = OrderPaymentWayForm(initial=initial)
        else:
            self.order_delivery_way_form = OrderDeliveryWayForm(request.POST)
            self.order_payment_way_form = OrderPaymentWayForm(request.POST)


        if 'order' in request.POST or 'update' in request.POST:
            # ted pujde potvrzeni, tj. nasledujici stav
            if 'order' in request.POST:
                self.order_stage_form = OrderStageForm(initial={'stage':1})
                if self.order_delivery_way_form.is_valid():
                    self.order_delivery_way_form.fields['delivery_way'].widget \
                        = widgets.HiddenInput({'value':self.order_delivery_way_form.cleaned_data['delivery_way'],
                                           })
                    self.order_delivery_way_form.fields['delivery_way'].widget.attrs['readonly'] = True
                if self.order_payment_way_form.is_valid():
                    self.order_payment_way_form.fields['payment_way'].widget \
                        = widgets.HiddenInput({'value':self.order_payment_way_form.cleaned_data['payment_way'],
                                           })
                    self.order_payment_way_form.fields['payment_way'].widget.attrs['readonly'] = True
            else:
                self.order_stage_form = OrderStageForm(initial={'stage':0})

            context = self.get_context_data(**kwargs)
            basket = context['basket']

            # vycisteni basket od automatickych polozek, ktere zavisi na objednavce
            basket.removeAdditionalItem(toBeRemoved = lambda item: 'by-order' in item.type)
            if self.order_delivery_way_form.is_valid():
                delivery_way = self.order_delivery_way_form.cleaned_data['delivery_way']
                basket.addAdditionalItem(DeliveryPrice.asAdditionalItemForBasket(delivery_way))

            if self.order_payment_way_form.is_valid():
                payment_way = self.order_payment_way_form.cleaned_data['payment_way']
                basket.addAdditionalItem(PaymentPrice.asAdditionalItemForBasket(payment_way))

            # jestli je uzivatel prihlasen a ma slevu, tak doplnime
            if request.user.is_authenticated() and request.user.getUserDiscount():
                price = (-1 * Decimal(basket.total_price) * \
                         Decimal("0.01") * \
                         Decimal(request.user.getUserDiscount())) \
                    .quantize(Decimal('0'), rounding=ROUND_HALF_UP)
                basket.addAdditionalItem( request.user.getUserDiscountAsAdditionalItem(price) )

        elif 'submit-order' in request.POST:
            self.order_invoicing_form = OrderInvoicingForm(request.POST)
            self.order_contact_form = OrderContactForm(request.POST)
            self.order_delivery_form = OrderDeliveryForm(request.POST)
            self.order_payment_form = OrderPaymentForm(request.POST)
            self.userform = UserForm(request.POST)
            self.orderform = OrderForm(request.POST)
            self.order_stage_form = OrderStageForm(request.POST)

            if self.order_invoicing_form.is_valid() and \
               self.order_contact_form.is_valid() and \
               self.order_delivery_form.is_valid() and \
               self.order_payment_form.is_valid() and \
               self.order_delivery_way_form.is_valid() and \
               self.order_payment_way_form.is_valid() and \
               self.order_stage_form.is_valid() and \
               self.orderform.is_valid() and self.userform.is_valid():
                
                context = self.get_context_data(**kwargs)
                basket = context['basket']
                
                # vycisteni basket od automatickych polozek, ktere zavisi na objednavce
                basket.removeAdditionalItem(toBeRemoved = lambda item: 'by-order' in item.type)
                for item in self.orderform.getAdditionalItems():
                    basket.addAdditionalItem(item)

                # jestli je uzivatel prihlasen a ma slevu, tak doplnime
                if request.user.is_authenticated() and request.user.getUserDiscount():
                    price = (-1 * Decimal(basket.total_price) * \
                             Decimal("0.01") * \
                             Decimal(request.user.getUserDiscount())) \
                        .quantize(Decimal('0'), rounding=ROUND_HALF_UP)
                    basket.addAdditionalItem( request.user.getUserDiscountAsAdditionalItem(price) )

                # ulozeni objednavky
                with transaction.commit_on_success():
                    order = self.orderform.save()
                    user = self.userform.save()
                    # ulozeni uzivatele do objednavky, pokud existuje
                    if user:
                        order.user = user
                        order.save()

                    # ulozeni polozek objednavky 
                    for item in basket.sell():
                        orderItem = OrderItem(order=order, item=item)
                        orderItem.save()
                    pass

                    # ulozeni dodatecnych polozek objednavky    
                    for additionalItem in basket.additional_items:
                        orderAdditionalItem = OrderAdditionalItem(order = order,
                                                                  description = additionalItem.desc,
                                                                  meta = additionalItem.type,
                                                                  price = additionalItem.price)
                        orderAdditionalItem.save()
                        pass
                    pass

                # redirect na podekovani
                context['order'] = order
                context['user'] = user
                    
                return render_to_response("eshop/order_thanks.html",
                                          context,
                                          context_instance=RequestContext(request))
        elif 'cancel' in request.POST:
            return redirect("/eshop")

        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

    render_to_response = prepare_render_to_response(JSONTemplateResponse, TemplateView)

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


def get_order_pdf(request,*args,**kwargs):
    context = Context({
        'PAYMENTS' : PAYMENT_WAYS,
        'DELIVERY' : DELIVERY_WAYS,
        'object' : Order.objects.get(pk=kwargs['pk'])
    })
    return render_to_pdf_response('eshop/invoice.html', 
                                  pdfname='invoice-%s' % (context['object'].id,), 
                                  context=context)

def sendTransitionEmail(subject, text, contact_email, order):
    from django.core.mail import EmailMultiAlternatives
    context = Context({
        'subject': subject,
        'text': text,
        'object':order, 
        'order': order,
        'PAYMENTS': PAYMENT_WAYS,
        'DELIVERY': DELIVERY_WAYS
    })
    htmlCode = loader.get_template('eshop/transitionemail.html').render(context)
    message = EmailMultiAlternatives(subject=subject,
                                     from_email='bazar@bazar-cd.cz',
                                     to=[contact_email,],
                                     bcc=['stavel.jan@gmail.com',])
    message.attach_alternative(text.encode('utf8'), 'text/plain')
    message.attach_alternative(htmlCode.encode('utf8'),'text/html')
    #print message.message().as_string()
    return message.send(fail_silently=False)
    
class OrderView(DetailView, JSONTemplateResponse):
    model = Order
    template_name = "eshop/order_detail.html"
    page_includes = ['eshop/order_detail/detail.html',
                     'eshop/order_detail/js.js',
                     'eshop/order_detail/actions.html',
                     'eshop/order_detail/form.html'
    ]

    def get_context_data(self,**kwargs):
        context = super(OrderView,self).get_context_data(**kwargs)
        context['form'] = getattr(self,'form',OrderTransitionForm())
        context['form'].fields['transition'].choices = [(0,'--- vyber si ---'),] + \
                                                       map(lambda tr: (tr,_(tr)), self.object.available_transitions())
        return context

    def get(self, request, *args, **kwargs):
        if request.REQUEST.get('update_user_discount',None):
            #import sys,pdb; pdb.Pdb(stdout=sys.__stdout__).set_trace()
            order = self.get_object()
            for additionalItem in filter(lambda item: item.meta=="by-order:user-discount", order.orderadditionalitem_set.all()):
                additionalItem.delete()
                pass
            if order.user and order.user.getUserDiscount():
                price = (-1 * order.total_price * Decimal("0.01") * Decimal(order.user.getUserDiscount())).quantize(Decimal('0'), rounding=ROUND_HALF_UP)
                additionalItem = request.user.getUserDiscountAsAdditionalItem(price)
                orderAdditionalItem = OrderAdditionalItem(order = order,
                                                          description = additionalItem.desc,
                                                          meta = additionalItem.type,
                                                          price = additionalItem.price)
                orderAdditionalItem.save()
            pass
        return super(OrderView,self).get(request,*args,**kwargs)

    def post(self, request, *args, **kwargs):
        self.success_url_form = SuccessURLForm(self.request.POST)
        self.form = OrderTransitionForm(request.POST)
        order = self.get_object()
        self.form.fields['transition'].choices = [(0,'--- vyber si ---'),] + \
                                                 map(lambda tr: (tr,_(tr)), order.available_transitions())
        if request.POST.get('submit',"") == u"načíst šablonu":
            def valueFactory(value):
                def value_from_datadict(data, files, prefix):
                    return value
                return value_from_datadict
            try:
                emailMessage = EmailMessage.objects.get(id=request.POST.get('emailMessageID',0))
                self.form.fields['subject'].widget.value_from_datadict = valueFactory(emailMessage.title)
                self.form.fields['message'].widget.value_from_datadict = valueFactory(emailMessage.text)
            except EmailMessage.DoesNotExist:
                self.form.fields['subject'].widget.value_from_datadict = valueFactory("")
                self.form.fields['message'].widget.value_from_datadict = valueFactory("")
                pass
        else:
            if self.form.is_valid():
                data = self.form.cleaned_data
                if data['subject'] and data['transition']:
                    sendTransitionEmail(data['subject'], 
                                        data['message'],
                                        order.contact_email, 
                                        order)
                    messages.add_message(request, messages.INFO, 'Odeslal jsem email.')
                
                # transition pro objednavku
                # print 'process transition: ', data['transition'], "\n"
                order.processTransition(data['transition'])
                order.save()

                if self.success_url_form.is_valid() and self.success_url_form.cleaned_data['success_url']:
                    return redirect(self.success_url_form.cleaned_data['success_url'])
                else:
                    return redirect("/eshop/order")
        return super(OrderView,self).get(request, *args, **kwargs)

    render_to_response = prepare_render_to_response(JSONTemplateResponse, DetailView)


class EmailMessageView(BaseDetailView):
    model = EmailMessage
    def render_to_response(self, context, **kwargs):
        return HttpResponse(json.dumps({'title': context['object'].title,
                                        'text': context['object'].text,
                                        'id': context['object'].id
                                    }), **kwargs)
