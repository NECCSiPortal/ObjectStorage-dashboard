#  Licensed under the Apache License, Version 2.0 (the "License"); you may
#  not use this file except in compliance with the License. You may obtain
#  a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#  WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#  License for the specific language governing permissions and limitations
#  under the License.
#
#  COPYRIGHT  (C)  NEC  CORPORATION  2016

import datetime
import os
import time
import traceback

from horizon.test import helpers as test

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait

# Command executor. Hub URL of Jenkins
SET_COMMAND_EXECUTOR = "http://xx.xx.xx.xx:4444/wd/hub"
# Base URL. Environment for testing.
# As for the URL, the last slash is unnecessary
# SET_BASE_URL = "http://xx.xx.xx.xx:8180/dashboard"
SET_BASE_URL = "http://xx.xx.xx.xx"
# Login user
SET_USERNM = "admin"
SET_PASSWORD = "xxxx"
SET_USERNM_USER = "demo"
SET_PASSWORD_USER = "xxxx"
# Take the capture
SET_CAPFLG = True
# Width of the window
SET_WIDTH = 1280
# Height of the window
SET_HEIGHT = 1024
# Implicitly wait & Timeout
SET_IMPLICITLY_WAIT = 90
SET_TIMEOUT = 10
# Capture of location
SET_CAPPATH = "openstack_dashboard/test/tests/screenshots/"
# Data prefix
SET_DATAPREFIX = "selenium_longname_ui_" + \
    datetime.datetime.today().strftime("%Y%m%d%H%M%S")
# They are arranged sequentially by setting the browser target
SET_BROWSER_LIST = {
    "firefox": {
        "browserName": "firefox",
        "version": "",
        "platform": "ANY",
        "javascriptEnabled": True,
    },
    "chrome": {
        "browserName": "chrome",
        "version": "",
        "platform": "ANY",
        "javascriptEnabled": True,
    },
    "ie11": {
        "browserName": "internet explorer",
        "version": "11",
        "platform": "WINDOWS",
        "javascriptEnabled": True,
    },
    "ie10": {
        "browserName": "internet explorer",
        "version": "10",
        "platform": "WINDOWS",
        "javascriptEnabled": True,
    },
}

# They are arranged sequentially by setting the execution target
SET_METHOD_LIST = [
    "change_setting",
    "sign_in",
    "bucket_lists",
    "bucket_lists_acl",
    "sign_out",
]

MAX_LENGTH_NUMBER = 4
MAX_LENGTH_DESCRIPTION = 255


class BrowserTests(test.SeleniumTestCase):
    """Selenium Test of Browser"""

    def setUp(self):
        """Setup selenium settings"""
        super(BrowserTests, self).setUp()

        # One setting of the browser is necessary
        # to carry out a test of selenium.
        key = SET_BROWSER_LIST.keys()[0]
        value = SET_BROWSER_LIST[key]

        print (value)
        self.caps = key
        self.selenium = webdriver.Remote(
            command_executor=SET_COMMAND_EXECUTOR,
            desired_capabilities=value)

        self.selenium.implicitly_wait(SET_IMPLICITLY_WAIT)

    def initialize(self):
        """Initializing process"""

        # Capture count
        self.cap_count = 1
        # Method name
        self.method = ""

    def test_main(self):
        """Main execution method"""
        try:
            # Datetime
            self.datetime = datetime.datetime.today().strftime("%Y%m%d%H%M%S")

            # Browser order definition
            for key, value in SET_BROWSER_LIST.items():
                if not self.caps == key:
                    self.caps = key
                    self.selenium = webdriver.Remote(
                        command_executor=SET_COMMAND_EXECUTOR,
                        desired_capabilities=value)

                    self.selenium.implicitly_wait(SET_IMPLICITLY_WAIT)

                # Browser display waiting time
                self.selenium.implicitly_wait(SET_IMPLICITLY_WAIT)
                # Set the size of the window
                self.selenium.set_window_size(SET_WIDTH, SET_HEIGHT)

                # Initializing process
                self.initialize()
                # Set object language
                self.multiple_languages = "en"
                # Call execution method
                self.is_admin = True
                self.execution()
                self.is_admin = False
                self.execution()

                # Initializing process
                self.initialize()
                # Set object language
                self.multiple_languages = "ja"
                # Call execution method
                self.is_admin = True
                self.execution()
                self.is_admin = False
                self.execution()

            print ("Test has been completed")

        except Exception:
            print ("Test failed")

    def execution(self):
        """Execution method"""
        # Method execution order definition
        for self.method in SET_METHOD_LIST:
            try:
                method = getattr(self, self.method)
                method()

                print (" Success:" + self.caps + " " +
                        self.multiple_languages + ":" + self.method)
            except Exception as e:
                print (" Failure:" + self.caps + " " +
                        self.multiple_languages + ":" + self.method +
                       ":" + e.message)
                print (traceback.print_exc())

    def save_screenshot(self):
        "Save a screenshot"
        if SET_CAPFLG:
            filepath = SET_CAPPATH + self.datetime + "/" + \
                self.multiple_languages + "/" + self.caps + "/"
            filename = str(self.cap_count).zfill(4) + \
                "_" + self.method + ".png"
            # Make directory
            if not os.path.isdir(filepath):
                os.makedirs(filepath)

            time.sleep(2)
            self.selenium.get_screenshot_as_file(filepath + filename)
            self.cap_count = self.cap_count + 1

    def trans_and_wait(self, nextId, urlpath, timeout=SET_TIMEOUT):
        """Transition to function"""
        self.selenium.get(SET_BASE_URL + urlpath)
        self.wait_id(nextId, timeout)

    def fill_field(self, field_id, value):
        """Enter a value to the field"""
        self.fill_field_clear(field_id)
        self.selenium.find_element_by_id(field_id).send_keys(value)

    def fill_field_by_name(self, field_name, value):
        """Enter a value to the field"""
        self.fill_field_clear_by_name(field_name)
        self.selenium.find_element_by_name(field_name).send_keys(value)

    def fill_field_by_css(self, css, value):
        """Enter a value to the css"""
        self.fill_field_clear_by_css(css)
        self.selenium.find_element_by_css_selector(css).send_keys(value)

    def fill_field_clear(self, field_id):
        """Clear to the field"""
        self.selenium.find_element_by_id(field_id).clear()

    def fill_field_clear_by_name(self, field_name):
        """Clear to the field"""
        self.selenium.find_element_by_name(field_name).clear()

    def fill_field_clear_by_css(self, css):
        """Clear to the css"""
        self.selenium.find_element_by_css_selector(css).clear()

    def click_and_wait(self, field_id, nextId, timeout=SET_TIMEOUT):
        """Click on the button"""
        element = self.selenium.find_element_by_id(field_id)
        element.click()
        self.wait_id(nextId, timeout)

    def click_id(self, field_id, timeout=SET_TIMEOUT):
        """Click on the button id(no wait)"""
        element = self.selenium.find_element_by_id(field_id)
        element.click()

    def click_name(self, field_name, timeout=SET_TIMEOUT):
        """Click on the button name(no wait)"""
        element = self.selenium.find_element_by_name(field_name)
        element.click()

    def click_link_text(self, link_text, timeout=SET_TIMEOUT):
        """Click on the link text(no wait)"""
        element = self.selenium.find_element_by_link_text(link_text)
        element.click()

    def click_css(self, css, timeout=SET_TIMEOUT):
        """Click on the button css(no wait)"""
        element = self.selenium.find_element_by_css_selector(css)
        element.click()

    def click_xpath(self, xpath, timeout=SET_TIMEOUT):
        """Click on the button xpath"""
        element = self.selenium.find_element_by_xpath(xpath)
        element.click()

    def click_css_and_ajax_wait(self, css, timeout=SET_TIMEOUT):
        """Click on the button css ajax wait"""
        element = self.selenium.find_element_by_css_selector(css)
        element.click()
        self.wait_ajax(timeout)

    def click_xpath_and_ajax_wait(self, xpath, timeout=SET_TIMEOUT):
        """Click on the button xpath ajax wait"""
        element = self.selenium.find_element_by_xpath(xpath)
        element.click()
        self.wait_ajax(timeout)

    def set_select_value(self, field_id, value):
        """Set of pull-down menu by value"""
        Select(self.selenium.find_element_by_id(field_id))\
            .select_by_value(value)

    def wait_id(self, nextId, timeout=SET_TIMEOUT):
        """Wait until the ID that you want to schedule is displayed"""
        WebDriverWait(self.selenium, timeout).until(
            EC.visibility_of_element_located((By.ID, nextId)))

    def wait_ajax(self, timeout=SET_TIMEOUT):
        """Wait until ajax request is completed"""
        WebDriverWait(self.selenium, timeout).until(
            lambda s: s.execute_script("return jQuery.active == 0"))

    def _change_page(self, table_id, save_screen):
        """Move next page and previous page.
        :param table_id: target table id.
        :param save_screen: Save screenshot image.
        """
        if not save_screen:
            return

        # Move next page
        self.click_css("#%s > tfoot > tr > td > a" % table_id)
        self.save_screenshot()

        # Move previous page
        self.click_css("#%s > tfoot > tr > td > a" % table_id)
        self.save_screenshot()

    def sign_in(self):
        """Sign In"""
        # Capture the initial display
        self.trans_and_wait("loginBtn", "")

        if self.is_admin:
            self.fill_field("id_username", SET_USERNM)
            self.fill_field("id_password", SET_PASSWORD)
        else:
            self.fill_field("id_username", SET_USERNM_USER)
            self.fill_field("id_password", SET_PASSWORD_USER)

        # self.click_and_wait("loginBtn", "date_form")
        self.click_id("loginBtn")
        time.sleep(3)

    def sign_out(self):
        """Sign Out"""
        self.trans_and_wait("loginBtn", "/dashboard/auth/logout/")
        time.sleep(3)

    def change_setting(self, page=2):
        """Change Language, pagesize page"""
        # Sign In
        self.sign_in()

        # Change Language
        self.trans_and_wait("id_pagesize", "/dashboard/settings/")
        self.fill_field("id_pagesize", page)
        self.set_select_value("id_language", self.multiple_languages)
        self.click_css("input.btn.btn-primary")

        # Sign Out
        self.sign_out()

    def bucket_lists(self, save_screen=True):
        """Show bucket list.
        :param save_screen: Save screenshot image.
        """
        # Show bucket lists
        self.trans_and_wait("bucket__row_Container_sample__action_update", "/dashboard/project/bucket_lists/")
        if save_screen:
            self.save_screenshot()

        # Filter
        self.fill_field_by_name("bucket__filter__q", "no_data")
        time.sleep(3)
        if save_screen:
            self.save_screenshot()

        self.fill_field_by_name("bucket__filter__q", "")
        time.sleep(3)
        if save_screen:
            self.save_screenshot()

    def bucket_lists_acl(self, save_screen=True):
        """Entry a bucket detail.
        :param save_screen: Save screenshot image.
        """
        # Show bucket lists
        self.trans_and_wait("bucket__row_Container_sample__action_update", "/dashboard/project/bucket_lists/")
        time.sleep(3)
        if save_screen:
            self.save_screenshot()

        # Show bucket detail
        self.click_id("bucket__row_Container_sample__action_update")
        time.sleep(3)
        if save_screen:
            self.save_screenshot()

        self.click_css("btn.btn-default.cancel")
        time.sleep(3)
        if save_screen:
            self.save_screenshot()

        # Show bucket detail
        self.click_id("bucket__row_Container_sample__action_update")
        time.sleep(3)
        if save_screen:
            self.save_screenshot()

        self.click_css("btn.btn-primary")
        time.sleep(3)
        if save_screen:
            self.save_screenshot()
