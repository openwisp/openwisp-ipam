from django.contrib.auth.models import Permission
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import tag
from django.urls import reverse
from openwisp_utils.tests.selenium import SeleniumTestMixin
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from . import CreateModelsMixin


@tag("selenium_tests")
class TestSubnetChangeViewSelenium(
    SeleniumTestMixin, CreateModelsMixin, StaticLiveServerTestCase
):
    app_label = "openwisp_ipam"

    def test_available_address_popup_respects_add_permission(self):
        subnet = self._create_subnet(subnet="10.0.0.0/29", description="Sample Subnet")
        staff_user = self._create_user(
            username="staff", password="tester", email="staff@staff.com", is_staff=True
        )
        staff_user.user_permissions.add(
            *Permission.objects.filter(codename__in=["view_subnet", "view_ipaddress"])
        )
        self._create_org_user(
            organization=subnet.organization, user=staff_user, is_admin=True
        )
        url = reverse(f"admin:{self.app_label}_subnet_change", args=[subnet.id])

        with self.subTest("without add permission"):
            self.login(username="staff", password="tester")
            self.open(url)
            address_element = self.find_element(By.CSS_SELECTOR, "a#addr_10001")
            address_element.click()
            self.assertEqual(len(self.web_driver.window_handles), 1)
        self.logout()

        with self.subTest("with add permission"):
            self.login()
            self.open(url)
            address_element = self.find_element(By.CSS_SELECTOR, "a#addr_10001")
            address_element.click()
            WebDriverWait(self.web_driver, 5).until(
                lambda driver: len(driver.window_handles) == 2
            )
            self.web_driver.switch_to.window(self.web_driver.window_handles[-1])
            self.assertIn(
                reverse(f"admin:{self.app_label}_ipaddress_add"),
                self.web_driver.current_url,
            )

    def test_available_address_popup_hidden_for_disabled_org(self):
        organization = self._create_org(name="disabled org", slug="disabled-org")
        subnet = self._create_disabled_org_subnet(
            organization=organization, subnet="10.72.0.0/29"
        )
        # Even a superuser must not be able to open a popup when the subnet's
        # organization is disabled.
        self.login()
        self.open(reverse(f"admin:{self.app_label}_subnet_change", args=[subnet.id]))
        address_element = self.find_element(By.CSS_SELECTOR, "a#addr_107201")
        self.assertEqual(
            address_element.get_attribute("title"),
            "Cannot create IP Address for a disabled organization.",
        )
        self.assertEqual(address_element.get_attribute("class"), "disabled")
        address_element.click()
        self.assertEqual(len(self.web_driver.window_handles), 1)
