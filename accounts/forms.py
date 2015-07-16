from django.utils.translation import ugettext as _
from django.contrib.auth.models import User
from .models import UserProfile
import django.forms as forms

class UserProfileAuthenticationForm(forms.Form):
    password1 = forms.CharField(label=_("Password"),
                                required = False,
                                widget=forms.PasswordInput)
    password2 = forms.CharField(label=_("Password confirmation"),
                                required = False,
                                widget=forms.PasswordInput,
                                help_text = _("Enter the same password as above, for verification."))
    
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

class UserProfileInvoicingForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('invoicing_firm',
                  'invoicing_name',
                  'invoicing_surname',
                  'invoicing_address_street',
                  'invoicing_address_zip',
                  'invoicing_address_city',
                  'invoicing_address_country',
                  'invoicing_address_ico',
                  'invoicing_address_dic',
                  )

class UserProfileContactForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('contact_email',
                  'contact_phonenumber',
                  )


class UserProfileDeliveryForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('delivery_way',
                  'delivery_firm',
                  'delivery_name',
                  'delivery_surname',
                  'delivery_address_street',
                  'delivery_address_zip',
                  'delivery_address_city',
                  'delivery_address_country',
                  )

class UserProfilePaymentForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('payment_way',
                  )
