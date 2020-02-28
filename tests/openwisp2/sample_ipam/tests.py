import os
from unittest import skipUnless

import swapper
from django.forms import ModelForm
from django.test import TestCase
from openwisp_ipam.tests.base.test_admin import BaseTestAdmin
from openwisp_ipam.tests.base.test_api import BaseTestApi
from openwisp_ipam.tests.base.test_commands import BaseTestCommands
from openwisp_ipam.tests.base.test_forms import BaseTestForms
from openwisp_ipam.tests.base.test_models import BaseTestModel
from openwisp_ipam.tests.base.test_multitenant import BaseTestMultitenant
from openwisp_users.tests.test_admin import TestUsersAdmin

IpAddress = swapper.load_model('sample_ipam', 'IPAddress')
Subnet = swapper.load_model('sample_ipam', 'Subnet')


@skipUnless(os.environ.get('SAMPLE_APP', False), 'Running tests on standard django-ipam models')
class TestAdmin(BaseTestAdmin, TestCase):
    app_name = 'sample_ipam'
    ipaddress_model = IpAddress
    subnet_model = Subnet


@skipUnless(os.environ.get('SAMPLE_APP', False), 'Running tests on standard django-ipam models')
class TestApi(BaseTestApi, TestCase):
    ipaddress_model = IpAddress
    subnet_model = Subnet


@skipUnless(os.environ.get('SAMPLE_APP', False), 'Running tests on standard django-ipam models')
class TestCommands(BaseTestCommands, TestCase):
    app_name = 'sample_ipam'
    subnet_model = Subnet
    ipaddress_model = IpAddress


@skipUnless(os.environ.get('SAMPLE_APP', False), 'Running tests on standard django-ipam models')
class NetworkAddressTestModelForm(ModelForm):
    class Meta:
        model = Subnet
        fields = ('subnet',)


@skipUnless(os.environ.get('SAMPLE_APP', False), 'Running tests on standard django-ipam models')
class TestForms(BaseTestForms, TestCase):
    form_class = NetworkAddressTestModelForm


@skipUnless(os.environ.get('SAMPLE_APP', False), 'Running tests on standard django-ipam models')
class TestModel(BaseTestModel, TestCase):
    ipaddress_model = IpAddress
    subnet_model = Subnet


@skipUnless(os.environ.get('SAMPLE_APP', False), 'Running tests on standard django-ipam models')
class TestMultitenantAdmin(BaseTestMultitenant, TestCase):
    app_name = 'sample_ipam'
    ipaddress_model = IpAddress
    subnet_model = Subnet


@skipUnless(os.environ.get('SAMPLE_APP', False), 'Running tests on standard django-ipam models')
class TestUsersIntegration(TestUsersAdmin):
    pass


del TestUsersAdmin
