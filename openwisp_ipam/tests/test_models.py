from ipaddress import IPv4Network, IPv6Network

from django.core.exceptions import ValidationError
from django.test import TestCase
from swapper import load_model

from . import CreateModelsMixin

Subnet = load_model('openwisp_ipam', 'Subnet')
IpAddress = load_model('openwisp_ipam', 'IpAddress')


class TestModel(CreateModelsMixin, TestCase):
    def test_ip_address_string_representation(self):
        ipaddress = IpAddress(ip_address='entry ip_address')
        self.assertEqual(str(ipaddress), ipaddress.ip_address)

    def test_invalid_ipaddress_subnet(self):
        self._create_subnet(subnet='192.168.2.0/24')
        try:
            self._create_ipaddress(ip_address='10.0.0.2', subnet=Subnet.objects.first())
        except ValidationError as e:
            self.assertTrue(e.message_dict['ip_address'] == ['IP address does not belong to the subnet'])
        else:
            self.fail('ValidationError not raised')

    def test_valid_ipaddress_subnet(self):
        self._create_subnet(subnet='192.168.2.0/24')
        try:
            self._create_ipaddress(
                ip_address='192.168.2.1', subnet=Subnet.objects.first()
            )
        except ValidationError:
            self.fail('ValidationError raised')

    def test_used_ipaddress(self):
        self._create_subnet(subnet='10.0.0.0/24')
        self._create_ipaddress(ip_address='10.0.0.1', subnet=Subnet.objects.first())
        try:
            self._create_ipaddress(ip_address='10.0.0.1', subnet=Subnet.objects.first())
        except ValidationError as e:
            self.assertTrue(
                e.message_dict['ip_address'] == ['IP address already used.']
            )
        else:
            self.fail('ValidationError not raised')

    def test_invalid_ipaddress(self):
        error_message = "'1234325' does not appear to be an IPv4 or IPv6 address"
        self._create_subnet(subnet='10.0.0.0/24')
        try:
            self._create_ipaddress(ip_address='1234325', subnet=Subnet.objects.first())
        except ValueError as e:
            self.assertEqual(str(e), error_message)
        else:
            self.fail('ValueError not raised')

    def test_available_ipv4(self):
        subnet = self._create_subnet(subnet='10.0.0.0/24')
        self._create_ipaddress(ip_address='10.0.0.1', subnet=subnet)
        ipaddr = subnet.get_next_available_ip()
        self.assertEqual(str(ipaddr), '10.0.0.2')

    def test_available_ipv6(self):
        subnet = self._create_subnet(subnet='fdb6:21b:a477::9f7/64')
        self._create_ipaddress(ip_address='fdb6:21b:a477::1', subnet=subnet)
        ipaddr = subnet.get_next_available_ip()
        self.assertEqual(str(ipaddr), 'fdb6:21b:a477::2')

    def test_unavailable_ip(self):
        subnet = self._create_subnet(subnet='10.0.0.0/32')
        ipaddr = subnet.get_next_available_ip()
        self.assertEqual(ipaddr, None)

    def test_request_ipv4(self):
        subnet = self._create_subnet(subnet='10.0.0.0/24')
        self._create_ipaddress(ip_address='10.0.0.1', subnet=subnet)
        ipaddr = subnet.request_ip()
        self.assertEqual(str(ipaddr), '10.0.0.2')

    def test_request_ipv6(self):
        subnet = self._create_subnet(subnet='fdb6:21b:a477::9f7/64')
        self._create_ipaddress(ip_address='fdb6:21b:a477::1', subnet=subnet)
        ipaddr = subnet.request_ip()
        self.assertEqual(str(ipaddr), 'fdb6:21b:a477::2')

    def test_unavailable_request_ip(self):
        subnet = self._create_subnet(subnet='10.0.0.0/32')
        ipaddr = subnet.request_ip()
        self.assertEqual(ipaddr, None)

    def test_subnet_string_representation(self):
        subnet = Subnet(subnet='entry subnet')
        self.assertEqual(str(subnet), str(subnet.subnet))

    def test_subnet_string_representation_with_name(self):
        subnet = Subnet(subnet='entry subnet', name='test1')
        self.assertEqual(str(subnet), '{0} {1}'.format(subnet.name, str(subnet.subnet)))

    def test_valid_cidr_field(self):
        try:
            self._create_subnet(subnet='22.0.0.0/24')
        except ValidationError:
            self.fail('ValidationError raised')

    def test_invalid_cidr_field(self):
        error_message = [
            "'192.192.192.192.192' does not appear to be an IPv4 or IPv6 network"
        ]
        try:
            self._create_subnet(subnet='192.192.192.192.192')
        except ValidationError as e:
            self.assertTrue(e.message_dict['subnet'] == error_message)
        else:
            self.fail('ValidationError not raised')

    def test_overlapping_subnet(self):
        self._create_subnet(subnet='192.168.2.0/24')
        try:
            self._create_subnet(subnet='192.168.2.0/25')
        except ValidationError as e:
            self.assertTrue(
                e.message_dict['subnet'] == ['Subnet overlaps with 192.168.2.0/24']
            )
        else:
            self.fail('ValidationError not raised')

    def test_invalid_master_subnet(self):
        subnet = self._create_subnet(subnet='10.20.0.0/24')
        try:
            self._create_subnet(subnet='192.168.2.0/24', master_subnet=subnet)
        except ValidationError as e:
            self.assertTrue(
                e.message_dict['master_subnet'] == ['Invalid master subnet']
            )
        else:
            self.fail('ValidationError not raised')

    def test_valid_subnet_relation_tree(self):
        subnet1 = self._create_subnet(subnet='12.0.56.0/24')
        try:
            subnet2 = self._create_subnet(subnet='12.0.56.0/25', master_subnet=subnet1)
            self._create_subnet(subnet='12.0.56.0/26', master_subnet=subnet2)
        except ValidationError:
            self.fail('Correct master_subnet not accepted')

    def test_invalid_subnet_relation_tree(self):
        subnet1 = self._create_subnet(subnet='12.0.56.0/24')
        self._create_subnet(subnet='12.0.56.0/25', master_subnet=subnet1)
        try:
            self._create_subnet(subnet='12.0.56.0/26', master_subnet=subnet1)
        except ValidationError as e:
            self.assertEqual(
                e.message_dict['subnet'], ['Subnet overlaps with 12.0.56.0/25']
            )
        else:
            self.fail('ValidationError not raised')

    def test_save_none_subnet_fails(self):
        try:
            self._create_subnet(subnet=None)
        except ValidationError as err:
            self.assertTrue(
                err.message_dict['subnet'] == ['This field cannot be null.']
            )
        else:
            self.fail('ValidationError not raised')

    def test_save_blank_subnet_fails(self):
        try:
            self._create_subnet(subnet='')
        except ValidationError as err:
            self.assertTrue(
                err.message_dict['subnet'] == ['This field cannot be blank.']
            )
        else:
            self.fail('ValidationError not raised')

    def test_retrieves_ipv4_ipnetwork_type(self):
        instance = self._create_subnet(subnet='10.1.2.0/24')
        instance = Subnet.objects.get(pk=instance.pk)
        self.assertIsInstance(instance.subnet, IPv4Network)

    def test_retrieves_ipv6_ipnetwork_type(self):
        instance = self._create_subnet(subnet='2001:db8::0/32')
        instance = Subnet.objects.get(pk=instance.pk)
        self.assertIsInstance(instance.subnet, IPv6Network)

    def test_incompatible_ipadresses(self):
        instance = self._create_subnet(subnet='10.1.2.0/24')
        try:
            self._create_subnet(subnet='2001:db8::0/32', master_subnet=instance)
        except TypeError as err:
            self.assertEqual(
                str(err), '2001:db8::/32 and 10.1.2.0/24 are not of the same version'
            )
        else:
            self.fail('TypeError not raised')

    def test_ipadresses_missing_attribute(self):
        instance = self._create_subnet(subnet='10.1.2.0/24')
        instance2 = self._create_subnet(subnet='10.1.3.0/25')
        del instance.subnet.network_address
        try:
            instance2.subnet.subnet_of(instance.subnet)
        except AttributeError as err:
            self.assertIn(
                str(err), '\'IPv4Network\' object has no attribute \'network_address\''
            )
        else:
            self.fail('TypeError not raised')
