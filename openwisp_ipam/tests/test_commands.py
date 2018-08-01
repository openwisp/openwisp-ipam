import swapper
from django.test import TestCase

from django_ipam.tests.base.test_commands import BaseTestCommands


class TestCommands(BaseTestCommands, TestCase):
    app_name = 'openwisp_ipam'
    subnet_model = swapper.load_model('openwisp_ipam', 'Subnet')
    ipaddress_model = swapper.load_model('openwisp_ipam', 'IpAddress')
