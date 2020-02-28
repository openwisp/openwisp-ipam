import os
from unittest import skipIf

import swapper
from django.forms import ModelForm
from django.test import TestCase
from openwisp_users.tests.test_admin import TestUsersAdmin

from .base.test_admin import BaseTestAdmin
from .base.test_api import BaseTestApi
from .base.test_commands import BaseTestCommands
from .base.test_forms import BaseTestForms
from .base.test_models import BaseTestModel
from .base.test_multitenant import BaseTestMultitenant

IpAddress = swapper.load_model('openwisp_ipam', 'IPAddress')
Subnet = swapper.load_model('openwisp_ipam', 'Subnet')


@skipIf(os.environ.get('SAMPLE_APP', False), 'Running tests on SAMPLE_APP')
class TestAdmin(BaseTestAdmin, TestCase):
    app_name = 'openwisp_ipam'
    ipaddress_model = IpAddress
    subnet_model = Subnet


@skipIf(os.environ.get('SAMPLE_APP', False), 'Running tests on SAMPLE_APP')
class TestApi(BaseTestApi, TestCase):
    ipaddress_model = IpAddress
    subnet_model = Subnet


@skipIf(os.environ.get('SAMPLE_APP', False), 'Running tests on SAMPLE_APP')
class TestCommands(BaseTestCommands, TestCase):
    app_name = 'openwisp_ipam'
    subnet_model = Subnet
    ipaddress_model = IpAddress


@skipIf(os.environ.get('SAMPLE_APP', False), 'Running tests on SAMPLE_APP')
class NetworkAddressTestModelForm(ModelForm):
    class Meta:
        model = Subnet
        fields = ('subnet',)


@skipIf(os.environ.get('SAMPLE_APP', False), 'Running tests on SAMPLE_APP')
class TestForms(BaseTestForms, TestCase):
    form_class = NetworkAddressTestModelForm


@skipIf(os.environ.get('SAMPLE_APP', False), 'Running tests on SAMPLE_APP')
class TestModel(BaseTestModel, TestCase):
    ipaddress_model = IpAddress
    subnet_model = Subnet


@skipIf(os.environ.get('SAMPLE_APP', False), 'Running tests on SAMPLE_APP')
class TestMultitenantAdmin(BaseTestMultitenant, TestCase):
    app_name = 'openwisp_ipam'
    ipaddress_model = IpAddress
    subnet_model = Subnet


@skipIf(os.environ.get('SAMPLE_APP', False), 'Running tests on SAMPLE_APP')
class TestUsersIntegration(TestUsersAdmin):
    pass


del TestUsersAdmin
