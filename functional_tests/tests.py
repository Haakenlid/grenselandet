# -*- coding: utf-8 -*-
""" Functional tests universitas.no """
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from django.contrib.staticfiles.testing import StaticLiveServerCase
from django.conf import settings
from os import path

PHANTOMJS_EXECUTABLE_PATH = '/home/haakenlid/node_modules/phantomjs/lib/phantom/bin/phantomjs'
PHANTOMJS_LOG_PATH = path.join(settings.LOG_FOLDER, 'phantom.log')
# PHANTOMJS_LOG_PATH = settings.LOG_FOLDER


WEBDRIVER = 'PhantomJS'
# WEBDRIVER = 'Firefox'


class FrontPageVisitTest(StaticLiveServerCase):

    def setUp(self):
        # TODO: load mocks∕fixtures of frontpage articles.
        if WEBDRIVER == 'PhantomJS':
            self.browser = webdriver.PhantomJS(
                service_log_path=PHANTOMJS_LOG_PATH,
                executable_path=PHANTOMJS_EXECUTABLE_PATH,
            )
        else:
            self.browser = webdriver.Firefox()

    def tearDown(self):
        self.browser.quit()

    def test_visitor_frontpage(self):
        # Ole-Petter har hørt at Universitas har fått en ny nettside.
        # Han skriver inn “http://universitas.no” i nettleseren for å se.
        self.browser.get(self.live_server_url)
