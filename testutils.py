# -*- coding: utf-8 -*-

from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.common.exceptions import NoSuchElementException
from django.test import LiveServerTestCase


class SeleniumTestCase(LiveServerTestCase):
    IMPLICITLY_WAIT = 5

    @classmethod
    def setUpClass(cls):
        cls.driver = WebDriver()
        cls.driver.implicitly_wait(SeleniumTestCase.IMPLICITLY_WAIT)
        super(SeleniumTestCase, cls).setUpClass()
        activate("cs")

    @classmethod
    def tearDownClass(cls):
        super(SeleniumTestCase, cls).tearDownClass()
        cls.driver.quit()

    def open_url(self, url):
        self.driver.get(self.live_server_url + url)

    def dumpdata(self, app_name, fpath):
        """ useful function to create fixtures.
        put breakpoint and call self.dumpdata(app_name,'/tmp/fixtures')
        """
        stdout = sys.stdout
        output = open(fpath,'w')
        sys.stdout = output

        # command prints out a result at stdout
        call_command('dumpdata',app_name)
        sys.stdout = stdout
        output.close()

    def fill_form(self, **kwargs):
        """ fill form. kwargs are id of input elements.
        If value is callable, so it is getter of the value.
        Arguments of the getter to be supposed:
            testcase,driver

        The function returns filled form data.
        """
        filled_form = {}
        for key, value in kwargs.items():
            if callable(value):
                got_value = value(self,self.driver)
                filled_form[key] = got_value
            else:
                elem = self.driver.find_element_by_id(key)
                elem.send_keys(value)
                filled_form[key] = value
        return filled_form

    def wait_till( self, must_wait, num_of_repeats=10, interval=1 ):
        """ iterate predicate must_wait till it returns True.
        After the predicate returns False it finish.
        If num of repeats overflows, it finish silently"""
        
        for count in range(num_of_repeats):
            if must_wait():
                time.sleep(interval)
            else:
                return None
        return None
        
    def gb_id(self, id):
        return self.driver.find_element_by_id(id)

    def gb_css(self, selector):
        return self.driver.find_element_by_css_selector(selector)

    def gb_xpath(self, path):
        return self.driver.find_element_by_xpath(path)

    def gb_link_text(self, text):
        return self.driver.find_element_by_link_text(text)


def with_no_wait(method):
    def no_wait(self,*args):
        self.driver.implicitly_wait(0)
        try:
            return method(self,*args)
        except NoSuchElementException,e:
            return None
        finally:
            self.driver.implicitly_wait(SeleniumTestCase.IMPLICITLY_WAIT)
            pass
    return no_wait


""" methods that will not wait either one sec. At the timeout the methods return None """
SeleniumTestCase.gb_xpath_nw = with_no_wait(SeleniumTestCase.gb_xpath)
SeleniumTestCase.gb_link_text_nw = with_no_wait(SeleniumTestCase.gb_link_text)
SeleniumTestCase.gb_css_nw = with_no_wait(SeleniumTestCase.gb_css)
SeleniumTestCase.gb_id_nw = with_no_wait(SeleniumTestCase.gb_id)

