# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from cdbazar.eshop.models import DELIVERY_WAYS, PAYMENT_WAYS
from django.utils.translation import ugettext as _

class UserProfile(models.Model):  
    user = models.OneToOneField(User)  

    #other fields here
    invoicing_firm = models.CharField(_('Firm'), max_length = 30, blank=True, null=True )
    invoicing_name = models.CharField(_('Name'), max_length = 30, blank=True, null=True)
    invoicing_surname = models.CharField(_('Surname'), max_length = 30, blank=True, null=True)
    invoicing_address_street = models.CharField(_("Street"), max_length = 30, blank=True, null=True)
    invoicing_address_zip = models.CharField(_("ZIP code"), max_length = 30, blank=True, null=True)
    invoicing_address_city = models.CharField(_("City"), max_length = 30, blank=True, null=True)
    invoicing_address_country = models.CharField(_("Country"), max_length = 30, blank=True, null=True)
    invoicing_address_ico = models.CharField(_("ICO"), max_length = 30, blank=True, null=True)
    invoicing_address_dic = models.CharField(_("VAT number"), max_length = 30, blank=True, null=True)
    
    contact_email = models.EmailField(_("Email"), max_length=30, blank=True, null=True)
    contact_phonenumber = models.CharField(_("Phone number"), max_length=30, blank=True, null=True)

    delivery_way = models.PositiveSmallIntegerField(_("Delivery way"), choices=DELIVERY_WAYS, default=1)
    delivery_firm = models.CharField(_('Firm'), max_length = 30, blank=True, null=True )
    delivery_name = models.CharField(_('Name'), max_length = 30, blank=True, null=True)
    delivery_surname = models.CharField(_('Surname'), max_length = 30, blank=True, null=True )
    delivery_address_street = models.CharField(_("Street"), max_length = 30, blank=True, null=True)
    delivery_address_zip = models.CharField(_("ZIP code"), max_length = 30, blank=True, null=True)
    delivery_address_city = models.CharField(_("City"), max_length = 30, blank=True, null=True)
    delivery_address_country = models.CharField(_("Country"), max_length = 30, blank=True, null=True)

    payment_way = models.PositiveSmallIntegerField(_("Payment way"), choices=PAYMENT_WAYS, default=1)

    def __str__(self):  
          return "%s's profile" % self.user  
 
def create_user_profile(sender, instance, created, **kwargs):  
    if created:  
       profile, created = UserProfile.objects.get_or_create(user=instance)  
 
post_save.connect(create_user_profile, sender=User) 
