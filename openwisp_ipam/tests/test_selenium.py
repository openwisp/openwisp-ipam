from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import tag
from django.urls import reverse
from openwisp_utils.tests import SeleniumTestMixin
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from . import CreateModelsMixin


@tag("selenium_tests")
class TestSubnet(SeleniumTestMixin, CreateModelsMixin, StaticLiveServerTestCase):
    app_label = "openwisp_ipam"

    def setUp(self):
        self._create_admin(username=self.admin_username, password=self.admin_password)

    def test_subnet_allocation_graph(self):
        subnet = self._create_subnet(subnet="10.0.0.0/29")
        used_subnet = self._create_subnet(subnet="10.0.0.1/32", master_subnet=subnet)
        self._create_subnet(subnet="10.0.0.2/32", master_subnet=subnet)
        self._create_ipaddress(ip_address="10.0.0.1", subnet=used_subnet)
        self.login()
        self.open(reverse(f"admin:{self.app_label}_subnet_change", args=[subnet.id]))
        self.wait_until(EC.invisibility_of_element_located((By.ID, "graph-loading")))
        reserved = self.find_element(
            by=By.XPATH,
            value='//*[@id="graph"]//*[text()="Reserved"]',
        )
        self.assertEqual(reserved.text, "Reserved")
        trace = reserved.parent.execute_script(
            "var trace = document.getElementById('graph').data[0];"
            "return {"
            "colors: trace.marker.colors,"
            "customdata: trace.customdata,"
            "hovertemplate: trace.hovertemplate,"
            "labels: trace.labels,"
            "text: trace.text || null,"
            "textinfo: trace.textinfo,"
            "values: trace.values"
            "};"
        )
        version = reserved.parent.execute_script("return Plotly.version;")
        self.assertEqual(version, "2.35.2")
        self.assertEqual(trace["values"], [4, 1, 1])
        self.assertEqual(trace["labels"], ["Available", "Reserved", "Used"])
        self.assertEqual(trace["colors"], ["#498b26", "#ffb442", "#a72d1d"])
        self.assertEqual(trace["customdata"], ["available", "reserved", "used"])
        self.assertIsNone(trace["text"])
        self.assertEqual(trace["textinfo"], "percent")
        self.assertEqual(
            trace["hovertemplate"],
            "%{value:,.0f} %{customdata} addresses (%{percent:.2%})<extra></extra>",
        )
        reserved_slice = self.find_element(
            by=By.CSS_SELECTOR,
            value="#graph .slice:nth-child(2) path",
        )
        reserved_slice.parent.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});", reserved_slice
        )
        ActionChains(reserved_slice.parent).move_to_element(reserved_slice).perform()
        self.wait_until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, ".hovertext"))
        )
        tooltip = self.find_element(by=By.CSS_SELECTOR, value=".hovertext")
        self.assertEqual(tooltip.text, "1 reserved addresses (16.67%)")

    def test_subnet_visual_display(self):
        subnet = self._create_subnet(subnet="10.0.0.0/24")
        used_subnet = self._create_subnet(subnet="10.0.0.2/32", master_subnet=subnet)
        self._create_subnet(subnet="10.0.0.3/32", master_subnet=subnet)
        self._create_ipaddress(ip_address="10.0.0.2", subnet=used_subnet)
        self.login()
        self.open(reverse(f"admin:{self.app_label}_subnet_change", args=[subnet.id]))
        self.wait_until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "#subnet-visual .reserved")
            )
        )
        reserved = self.find_element(
            by=By.CSS_SELECTOR,
            value="#subnet-visual .reserved",
        )
        used = self.find_element(
            by=By.CSS_SELECTOR,
            value="#subnet-visual .used",
        )
        self.assertEqual(reserved.text, "10.0.0.3")
        self.assertEqual(used.text, "10.0.0.2")
        self.assertEqual(used.tag_name, "span")
        self.assertIsNone(used.get_attribute("href"))

    def test_ipv6_subnet_visual_display(self):
        subnet = self._create_subnet(subnet="2001:db8::/126")
        used_subnet = self._create_subnet(
            subnet="2001:db8::1/128", master_subnet=subnet
        )
        self._create_subnet(subnet="2001:db8::2/128", master_subnet=subnet)
        self._create_ipaddress(ip_address="2001:db8::1", subnet=used_subnet)
        self.login()
        self.open(reverse(f"admin:{self.app_label}_subnet_change", args=[subnet.id]))
        self.wait_until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "#subnet-visual .reserved")
            )
        )
        reserved = self.find_element(
            by=By.CSS_SELECTOR,
            value="#subnet-visual .reserved",
        )
        used = self.find_element(
            by=By.CSS_SELECTOR,
            value="#subnet-visual .used",
        )
        self.assertEqual(reserved.value_of_css_property("width"), "240px")
        self.assertEqual(used.value_of_css_property("width"), "240px")
