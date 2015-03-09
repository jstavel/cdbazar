# -*- coding: utf-8 -*-
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User
from .models import *
import django.forms as forms

BANNERS = (('tradeaction','Akce'),('new-articles',u"Nové zboží"))
VIEWS = (('articles',u"Zboží"), ('tabular-view',u"Tabulkový přehled"),('tradeaction','V akci'))
SORTS = (('by-newest',u"Od nejnovějšího"),('by-cheaper',u"Od nejlevnějšího"),('by-abc','Podle abecedy'))
ACTIONS = (('banner',u'banner'), 
           ('view',u'view change'), 
           ('sort',u'sort change'),
           ('page',u'page change'))

class ArticleListPageState(forms.Form):
    banner = forms.ChoiceField( choices = BANNERS, widget=forms.HiddenInput)
    view = forms.ChoiceField( choices = VIEWS, widget=forms.HiddenInput)
    sort = forms.ChoiceField( choices = SORTS, widget=forms.HiddenInput)
    page = forms.IntegerField( widget=forms.HiddenInput )
    action = forms.ChoiceField( choices = ACTIONS, widget=forms.HiddenInput)
    query = forms.CharField(max_length=128, required=False, widget=forms.HiddenInput)
    mediatype = forms.CharField(max_length=128, required=False, widget=forms.HiddenInput)

class OrderStageForm(forms.Form):
    stage = forms.IntegerField(label="stage", 
                               initial=0,
                               widget=forms.HiddenInput()
                               )

class SuccessURLForm(forms.Form):
    success_url = forms.CharField(label="success url",
                                  max_length = 120,
                                  widget=forms.HiddenInput()
                                  )

class OrderForm(forms.ModelForm):
    """ kompletni formular objednavky """
    class Meta:
        model = Order

    def getAdditionalItems(self):
        data = self.cleaned_data
        additionalItems = []
        additionalItems += [DeliveryPrice.asAdditionalItemForBasket(data['delivery_way'])]
        additionalItems += [PaymentPrice.asAdditionalItemForBasket(data['payment_way'])]
        return additionalItems

    def save(self):
        self.cleaned_data['state']=1
        self.instance.state = 1
        order = super(OrderForm,self).save(self)
        return order

    # def save(self):
    #     order = super(OrderForm,self).save(self)
    #     for additionalItem in self.getAdditionalItems():
    #         orderAdditionalItem = OrderAdditionalItem(order = order,
    #                                                   description = additionalItem.desc,
    #                                                   meta = additionalItem.type,
    #                                                   price = additionalItem.price)
    #         orderAdditionalItem.save()
    #     return order


class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields =  filter(lambda name: name != 'duedate' and name != 'created', 
                         map(lambda ff: ff.name, Reservation._meta.fields))

    # def save(self, commit=True):
    #     obj = super(forms.ModelForm,self).save()
    #     from datetime import timedelta
    #     obj.duedate = obj.created + timedelta(days=obj.duemonths*30)
    #     obj.save()
    #     return obj

class OrderInvoicingForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [ff.name for ff in Order._meta.fields if 'invoicing_' in ff.name]

class OrderContactForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [ff.name for ff in Order._meta.fields if 'contact_' in ff.name]

class OrderDeliveryWayForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [ff.name for ff in Order._meta.fields if 'delivery_way' in ff.name]

class OrderDeliveryForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [ff.name for ff in Order._meta.fields if 'delivery_' in ff.name and '_way' not in ff.name]

class OrderPaymentWayForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [ff.name for ff in Order._meta.fields if 'payment_way' in ff.name]

class OrderPaymentForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [ff.name for ff in Order._meta.fields if 'payment_' in ff.name and '_way' not in ff.name]

class OrderTransitionForm(forms.Form):
    transition = forms.ChoiceField(label="akce",
                                   required=False,
                                   choices = [(0,"--- akce ---")]
                               )
    emailMessageID = forms.ChoiceField(
        label = u"Šablona",
        required=False,
        choices = [(0,"--- select ---")] + [(msg.id, msg.title) for msg in EmailMessage.objects.all()],       
    )
    subject = forms.CharField(label="Titulek",
                              required = True,
                              )
    message = forms.CharField(label=u"Zpráva", 
                              required = True,
                              widget=forms.widgets.Textarea()
    )

    def __init__(self, *args, **kwargs):
        super(OrderTransitionForm,self).__init__(*args, **kwargs)
        self.fields['emailMessageID'].choices = [(0,"--- select ---")] \
                                                + [(msg.id, msg.title) for msg in EmailMessage.objects.all()]

class UserForm(forms.Form):
    # class Meta:
    #     model = User
    #     fields = ("username",)

    error_messages = {
        'duplicate_username': _("A user with that username already exists."),
        'password_mismatch': _("The two password fields didn't match."),
        'no username':_("Username is required"),
    }
    with_registration = forms.BooleanField(label=_("With registration"), 
                                           initial=True,
                                           required=False,
                                           )
    new_username = forms.RegexField(label=_("Username"), max_length=30,
                                required = False,
                                regex=r'^[\w.@+-]+$',
                                help_text = _("Required. max 30 characters or fewer. Letters, digits and "
                                              "@/./+/-/_ only."),
                                error_messages = {
                                    'invalid': _("This value may contain only letters, numbers and "
                                                 "@/./+/-/_ characters.")})
    password1 = forms.CharField(label=_("Password"),
                                required = False,
                                widget=forms.PasswordInput)
    password2 = forms.CharField(label=_("Password confirmation"),
                                required = False,
                                widget=forms.PasswordInput,
                                help_text = _("Enter the same password as above, for verification."))
    
    # def clean(self):
    #      """ at least one of email or phone number must be filled """
    #      cleaned_data = super(UserForm,self).clean()
    #      #import pdb; pdb.set_trace()
    #      if cleaned_data['with_registration'] and not cleaned_data['username']:
    #          raise forms.ValidationError(self.error_message['no username'])
    #      return cleaned_data

    def clean_new_username(self):
        # Since User.username is unique, this check is redundant,
        # but it sets a nicer error message than the ORM. See #13147.f
        username = self.cleaned_data["new_username"]
        if self.data.get('with_registration',False):
            try:
                User.objects.get(username=username)
            except User.DoesNotExist:
                return username
            raise forms.ValidationError(self.error_messages['duplicate_username'])
        return username
        

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1", "")
        password2 = self.cleaned_data["password2"]
        if password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'])
        return password2

    
    def save(self, commit=True):
        if self.cleaned_data['with_registration']:
            user = User.objects.create_user(self.cleaned_data['new_username'],
                                            email = self.data['contact_email'],
                                            password = self.data['password1'])
            if commit:
                user.save()
            return user
        return None
