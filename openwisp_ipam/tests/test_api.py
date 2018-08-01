import swapper
from django.test import TestCase

from django_ipam.tests.base.test_api import BaseTestApi


class TestApi(BaseTestApi, TestCase):
    ipaddress_model = swapper.load_model('openwisp_ipam', 'IPAddress')
    subnet_model = swapper.load_model('openwisp_ipam', 'Subnet')
