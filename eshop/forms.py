from django.utils.translation import ugettext as _
from django.contrib.auth.models import User
from .models import *
import django.forms as forms

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
    
    # def save(self):
    #     order = super(OrderForm,self).save(self)
    #     for additionalItem in self.getAdditionalItems():
    #         orderAdditionalItem = OrderAdditionalItem(order = order,
    #                                                   description = additionalItem.desc,
    #                                                   meta = additionalItem.type,
    #                                                   price = additionalItem.price)
    #         orderAdditionalItem.save()
    #     return order

class OrderInvoicingForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [ff.name for ff in Order._meta.fields if 'invoicing_' in ff.name]

class OrderContactForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [ff.name for ff in Order._meta.fields if 'contact_' in ff.name]

class OrderDeliveryForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [ff.name for ff in Order._meta.fields if 'delivery_' in ff.name]

class OrderPaymentForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [ff.name for ff in Order._meta.fields if 'payment_' in ff.name]

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("username",)

    error_messages = {
        'duplicate_username': _("A user with that username already exists."),
        'password_mismatch': _("The two password fields didn't match."),
        'no username':_("Username is required"),
    }
    with_registration = forms.BooleanField(label=_("With registration"), 
                                           initial=True,
                                           required=False,
                                           )
    username = forms.RegexField(label=_("Username"), max_length=30,
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

    def clean_username(self):
        # Since User.username is unique, this check is redundant,
        # but it sets a nicer error message than the ORM. See #13147.f
        username = self.cleaned_data["username"]
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
            user = super(UserForm, self).save(commit=False)
            user.set_password(self.cleaned_data["password1"])
            if commit:
                user.save()
            return user
        return None
