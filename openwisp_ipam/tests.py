import os
from unittest import skipIf

import swapper
from django.core.files.uploadedfile import SimpleUploadedFile
from django.forms import ModelForm
from django.test import TestCase
from django.urls import reverse

from django_ipam.tests.base.test_admin import BaseTestAdmin
from django_ipam.tests.base.test_api import BaseTestApi
from django_ipam.tests.base.test_commands import BaseTestCommands
from django_ipam.tests.base.test_forms import BaseTestForms
from django_ipam.tests.base.test_models import BaseTestModel

from .mixins import CreateModelsMixin, FileMixin, PostDataMixin


class TestAdmin(BaseTestAdmin, CreateModelsMixin, PostDataMixin, TestCase):
    app_name = 'openwisp_ipam'
    ipaddress_model = swapper.load_model('openwisp_ipam', 'IPAddress')
    subnet_model = swapper.load_model('openwisp_ipam', 'Subnet')

    def setUp(self):
        self._create_org()
        super(TestAdmin, self).setUp()

    def test_csv_upload(self):
        csv_data = """Monachers - Matera,
        10.27.1.0/24,
        Monachers,
        ,
        ip address,description
        10.27.1.1,Monachers
        10.27.1.252,NanoStation M5
        10.27.1.253,NanoStation M5
        10.27.1.254,Nano Beam 5 19AC"""
        csvfile = SimpleUploadedFile('data.csv', bytes(csv_data, 'utf-8'))
        response = self.client.post(reverse('admin:ipam_import_subnet'.format(self.app_name)),
                                    {'csvfile': csvfile}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(str(self.subnet_model.objects.first().subnet), '10.27.1.0/24')
        self.assertEqual(str(self.ipaddress_model.objects.all()[0].ip_address), '10.27.1.1')
        self.assertEqual(str(self.ipaddress_model.objects.all()[1].ip_address), '10.27.1.252')
        self.assertEqual(str(self.ipaddress_model.objects.all()[2].ip_address), '10.27.1.253')
        self.assertEqual(str(self.ipaddress_model.objects.all()[3].ip_address), '10.27.1.254')

    def test_existing_csv_data(self):
        subnet = self._create_subnet(name='Monachers - Matera', subnet='10.27.1.0/24')
        self._create_ipaddress(ip_address='10.27.1.1', subnet=subnet, description='Monachers')
        csv_data = """Monachers - Matera,
        10.27.1.0/24,
        test-organization,
        ,
        ip address,description
        10.27.1.1,Monachers
        10.27.1.252,NanoStation M5
        10.27.1.253,NanoStation M5
        10.27.1.254,Nano Beam 5 19AC"""
        csvfile = SimpleUploadedFile('data.csv', bytes(csv_data, 'utf-8'))
        response = self.client.post(reverse('admin:ipam_import_subnet'.format(self.app_name)),
                                    {'csvfile': csvfile}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(str(self.ipaddress_model.objects.all()[1].ip_address), '10.27.1.252')
        self.assertEqual(str(self.ipaddress_model.objects.all()[2].ip_address), '10.27.1.253')
        self.assertEqual(str(self.ipaddress_model.objects.all()[3].ip_address), '10.27.1.254')

    def test_invalid_ipaddress_csv_data(self):
        csv_data = """Monachers - Matera,
        10.27.1.0/24,
        Monachers,
        ,
        ip address,description
        10123142131,Monachers
        10.27.1.252,NanoStation M5
        10.27.1.253,NanoStation M5
        10.27.1.254,Nano Beam 5 19AC"""
        csvfile = SimpleUploadedFile('data.csv', bytes(csv_data, 'utf-8'))
        response = self.client.post(reverse('admin:ipam_import_subnet'.format(self.app_name)),
                                    {'csvfile': csvfile}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'does not appear to be an IPv4 or IPv6 address')


class TestApi(CreateModelsMixin, BaseTestApi, PostDataMixin, TestCase):
    ipaddress_model = swapper.load_model('openwisp_ipam', 'IPAddress')
    subnet_model = swapper.load_model('openwisp_ipam', 'Subnet')

    def setUp(self):
        self._create_org()
        super(TestApi, self).setUp()

    def test_import_subnet_api(self):
        csv_data = """Monachers - Matera,
        10.27.1.0/24,
        Monachers,
        ,
        ip address,description
        10.27.1.1,Monachers
        10.27.1.254,Nano Beam 5 19AC"""
        csvfile = SimpleUploadedFile('data.csv', bytes(csv_data, 'utf-8'))
        response = self.client.post(reverse('ipam:import-subnet'), {'csvfile': csvfile})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(str(self.subnet_model.objects.first().subnet), '10.27.1.0/24')
        self.assertEqual(str(self.ipaddress_model.objects.all()[0].ip_address), '10.27.1.1')
        self.assertEqual(str(self.ipaddress_model.objects.all()[1].ip_address), '10.27.1.254')

        csvfile = SimpleUploadedFile('data.txt', bytes(csv_data, 'utf-8'))
        response = self.client.post(reverse('ipam:import-subnet'),
                                    {'csvfile': csvfile}, follow=True)
        self.assertEqual(response.status_code, 400)
        csv_data = """Monachers - Matera,
        ,
        ,
        ip address,description
        10.27.1.1,Monachers
        10.27.1.254,Nano Beam 5 19AC"""
        invalid_file = SimpleUploadedFile('data.csv', bytes(csv_data, 'utf-8'))
        response = self.client.post(reverse('ipam:import-subnet'), {'csvfile': invalid_file})
        self.assertEqual(response.status_code, 400)


class TestCommands(CreateModelsMixin, BaseTestCommands, FileMixin, TestCase):
    app_name = 'openwisp_ipam'
    subnet_model = swapper.load_model('openwisp_ipam', 'Subnet')
    ipaddress_model = swapper.load_model('openwisp_ipam', 'IpAddress')


class NetworkAddressTestModelForm(ModelForm):
    class Meta:
        model = swapper.load_model('openwisp_ipam', 'Subnet')
        fields = ('subnet',)


@skipIf(os.environ.get('SAMPLE_APP', False), 'Running tests on SAMPLE_APP')
class TestForms(BaseTestForms, TestCase):
    form_class = NetworkAddressTestModelForm


class TestModel(BaseTestModel, CreateModelsMixin, TestCase):
    ipaddress_model = swapper.load_model('openwisp_ipam', 'IPAddress')
    subnet_model = swapper.load_model('openwisp_ipam', 'Subnet')
