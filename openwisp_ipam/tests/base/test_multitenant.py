from django.contrib.auth import get_user_model
from django.urls import reverse
from openwisp_users.tests.utils import TestMultitenantAdminMixin

from . import CreateModelsMixin

User = get_user_model()


class BaseTestMultitenant(TestMultitenantAdminMixin, CreateModelsMixin):

    def _create_multitenancy_test_env(self):
        org1 = self._create_org(name="test1organization")
        org2 = self._create_org(name="test2organization")
        subnet1 = self._create_subnet(
            subnet='172.16.0.1/16',
            organization=org1
        )
        subnet2 = self._create_subnet(
            subnet='192.168.0.1/16',
            organization=org2
        )
        ipadd1 = self._create_ipaddress(
            ip_address='172.16.0.1',
            organization=org1,
            subnet=subnet1

        )
        ipadd2 = self._create_ipaddress(
            ip_address='192.168.0.1',
            organization=org2,
            subnet=subnet2
        )
        operator = self._create_operator(organizations=[org1])
        data = dict(
            org1=org1, org2=org2,
            subnet1=subnet1, subnet2=subnet2,
            ipadd1=ipadd1, ipadd2=ipadd2,
            operator=operator
        )
        return data

    def test_multitenancy_ip_queryset(self):
        data = self._create_multitenancy_test_env()
        self._test_multitenant_admin(
            url=reverse(f'admin:{self.app_name}_ipaddress_changelist'),
            visible=[data['ipadd1']],
            hidden=[data['ipadd2']]
        )

    def test_multitenancy_subnet_queryset(self):
        data = self._create_multitenancy_test_env()
        self._test_multitenant_admin(
            url=reverse(f'admin:{self.app_name}_subnet_changelist'),
            visible=[data['subnet1']],
            hidden=[data['subnet2']]
        )
