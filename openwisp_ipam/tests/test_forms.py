import os
from unittest import skipIf

import swapper
from django.forms import ModelForm
from django.test import TestCase

from django_ipam.tests.base.test_forms import BaseTestForms


class NetworkAddressTestModelForm(ModelForm):
    class Meta:
        model = swapper.load_model('openwisp_ipam', 'Subnet')
        fields = ('subnet',)


@skipIf(os.environ.get('SAMPLE_APP', False), 'Running tests on SAMPLE_APP')
class TestForms(BaseTestForms, TestCase):
    form_class = NetworkAddressTestModelForm
