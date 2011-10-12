import logging

import test_utils
from functools import partial
from django.conf import settings
from django.core.urlresolvers import reverse
from django.test.client import Client


logging.disable(logging.INFO)


def get_absolute_uri(path):
    try:
        return settings.SITE_URL.rstrip('/') + path
    # For lazy reverse
    except TypeError:
        return settings.SITE_URL.rstrip('/') + path.format()


def reverse_absolute(*args, **kwargs):
    return get_absolute_uri(reverse(*args, **kwargs))


class TestClient(Client):

    def __getattr__(self, name):
        """
        Provides get_ajax, post_ajax, head_ajax methods etc in the
        test_client so that you don't need to specify the headers.
        """
        if name.endswith('_ajax'):
            method = getattr(self, name.split('_')[0])
            return partial(method, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        else:
            raise AttributeError


class TestCase(test_utils.TestCase):

    client_class = TestClient


try:
    from selenium import webdriver
    from selenium.webdriver.common.keys import Keys

    class BrowserTestCase(TestCase):

        url = None

        def goto_initial_url(self):
            self.browser.get(self.url)
            

        def setup_browser(self):
            self.browser = webdriver.Firefox()
            self.browser.implicitly_wait(5)
            if self.url:
                self.goto_initial_url()


        def setUp(self):
            super(BrowserTestCase, self).setUp()
            self.setup_browser()
            
        def tearDown(self):
            super(BrowserTestCase, self).tearDown()
            self.browser.close()

        def find(self, selector, context=None):
            """ Helper for getting elements by a CSS selector """
            if context:
                return context.find_elements_by_css_selector(selector)
            else:
                return self.browser.find_elements_by_css_selector(selector)


    class AsAnonMixin(object):
        pass


    class AsUserMixin(object):

        credentials = settings.TEST_CREDENTIALS['user']

        def __init__(self, *args, **kwargs):
            if not hasattr(self, 'fixtures'):
                self.fixtures = []
            self.fixtures.append('accounts/users.json')
            super(AsUserMixin, self).__init__(*args, **kwargs)

        def goto_initial_url(self):
            self.browser.get(get_absolute_uri(settings.LOGIN_URL))

            username_field = self.browser.find_element_by_name('username')
            username_field.send_keys(self.credentials['username'])

            password_field = self.browser.find_element_by_name('password')
            password_field.send_keys(self.credentials['password'])
            password_field.send_keys(Keys.RETURN)

            self.browser.get(self.url)


    class AsAdminMixin(AsUserMixin):

        credentials = settings.TEST_CREDENTIALS['admin']


except ImportError:
    pass
