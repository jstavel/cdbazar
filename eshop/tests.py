"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
import time

from cdbazar.testutils import SeleniumTestCase
class BasketReviewTests(SeleniumTestCase):
    
    def test_fill_form(self):
        self.open_url(reverse('site_root') + "/eshop/basket")
        pass



