from django.utils.translation import ugettext as _
from django.contrib.auth.models import User
from .models import DELIVERY_WAYS, Order, PAYMENT_WAYS
import django.forms as forms

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("username",)

    error_messages = {
        'duplicate_username': _("A user with that username already exists."),
        'password_mismatch': _("The two password fields didn't match."),
    }
    username = forms.RegexField(label=_("Username"), max_length=30,
                                regex=r'^[\w.@+-]+$',
                                help_text = _("Required. max 30 characters or fewer. Letters, digits and "
                                              "@/./+/-/_ only."),
                                error_messages = {
            'invalid': _("This value may contain only letters, numbers and "
                         "@/./+/-/_ characters.")})
    password1 = forms.CharField(label=_("Password"),
                                widget=forms.PasswordInput)
    password2 = forms.CharField(label=_("Password confirmation"),
                                widget=forms.PasswordInput,
                                help_text = _("Enter the same password as above, for verification."))
    
    # def clean_contact_phonenumber (self):
    #     pass

    # def clean(self):
    #     """ at least one of email or phone number must be filled """
    #     pass

    # def clean_username(self):
    #     # Since User.username is unique, this check is redundant,
    #     # but it sets a nicer error message than the ORM. See #13147.f
    #     import pdb; pdb.set_trace()
    #     username = self.cleaned_data["username"]
    #     try:
    #         User.objects.get(username=username)
    #     except User.DoesNotExist:
    #         return username
    #     raise forms.ValidationError(self.error_messages['duplicate_username'])

    # def clean_password2(self):
    #     import pdb; pdb.set_trace()
    #     password1 = self.cleaned_data.get("password1", "")
    #     password2 = self.cleaned_data["password2"]
    #     if password1 != password2:
    #         raise forms.ValidationError(
    #             self.error_messages['password_mismatch'])
    #     return password2

    
    def save(self, commit=True):
        import pdb; pdb.set_trace()
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


