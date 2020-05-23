import json

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from swapper import load_model

from . import CreateModelsMixin, PostDataMixin

User = get_user_model()
Subnet = load_model('openwisp_ipam', 'Subnet')
IpAddress = load_model('openwisp_ipam', 'IpAddress')


class TestApi(CreateModelsMixin, PostDataMixin, TestCase):
    def setUp(self):
        User.objects.create_superuser(
            username='admin', password='tester', email='admin@admin.com'
        )
        self.client.login(username='admin', password='tester')
        self._create_org()

    def test_ipv4_get_avaialble_api(self):
        subnet = self._create_subnet(subnet='10.0.0.0/24')
        self._create_ipaddress(ip_address='10.0.0.1', subnet=subnet)
        response = self.client.get(
            reverse('ipam:get_next_available_ip', args=(subnet.id,))
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '10.0.0.2')

    def test_ipv6_get_avaialble_api(self):
        subnet = self._create_subnet(subnet='fdb6:21b:a477::9f7/64')
        self._create_ipaddress(ip_address='fdb6:21b:a477::1', subnet=subnet)
        response = self.client.get(
            reverse('ipam:get_next_available_ip', args=(subnet.id,))
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'fdb6:21b:a477::2')

    def test_unavailable_ip(self):
        subnet = self._create_subnet(subnet='10.0.0.0/32', description='Sample Subnet')
        response = self.client.get(
            reverse('ipam:get_next_available_ip', args=(subnet.id,))
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, None)

    def test_ipv4_request_api(self):
        subnet = self._create_subnet(subnet='10.0.0.0/24')
        self._create_ipaddress(ip_address='10.0.0.1', subnet=subnet)
        post_data = self._post_data(subnet=str(subnet.id), description='Testing')
        response = self.client.post(
            reverse('ipam:request_ip', args=(subnet.id,)),
            data=post_data,
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['ip_address'], '10.0.0.2')

    def test_ipv6_request_api(self):
        subnet = self._create_subnet(subnet='fdb6:21b:a477::9f7/64')
        self._create_ipaddress(ip_address='fdb6:21b:a477::1', subnet=subnet)
        post_data = self._post_data(subnet=str(subnet.id), description='Testing')
        response = self.client.post(
            reverse('ipam:request_ip', args=(subnet.id,)),
            data=post_data,
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['ip_address'], 'fdb6:21b:a477::2')

    def test_unvailable_request_api(self):
        subnet = self._create_subnet(subnet='10.0.0.0/32')
        post_data = self._post_data(subnet=str(subnet.id), description='Testing')
        response = self.client.post(
            reverse('ipam:request_ip', args=(subnet.id,)),
            data=post_data,
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, None)

    def test_create_subnet_api(self):
        post_data = self._post_data(subnet='10.0.0.0/32', description='Testing')
        response = self.client.post(
            reverse('ipam:subnet_list_create'),
            data=post_data,
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(str(Subnet.objects.first().subnet), '10.0.0.0/32')

    def test_overlapping_subnet(self):
        post_data = self._post_data(
            subnet='10.20.0.0/24',
            name='Subnet',
            description='Sample',
            master_subnet='10.20.0.0/24',
        )
        response = self.client.post(
            reverse('ipam:subnet_list_create'),
            data=post_data,
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 400)

    def test_read_subnet_api(self):
        subnet_id = self._create_subnet(subnet='fdb6:21b:a477::/64').id
        response = self.client.get(reverse('ipam:subnet', args=(subnet_id,)))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['subnet'], 'fdb6:21b:a477::/64')

    def test_update_subnet_api(self):
        subnet_id = self._create_subnet(subnet='fdb6:21b:a477::9f7/64').id
        response = self.client.patch(
            reverse('ipam:subnet', args=(subnet_id,)),
            data=json.dumps({'description': 'Test Subnet'}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Subnet.objects.get(pk=subnet_id).description, 'Test Subnet')

    def test_delete_subnet_api(self):
        subnet_id = self._create_subnet(subnet='10.0.0.0/32').id
        response = self.client.delete(reverse('ipam:subnet', args=(subnet_id,)))
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Subnet.objects.count(), 0)

    def test_create_ip_address_api(self):
        subnet_id = self._create_subnet(subnet='10.0.0.0/24').id
        post_data = self._post_data(
            ip_address='10.0.0.2', subnet=str(subnet_id), description='Testing'
        )
        response = self.client.post(
            reverse('ipam:list_create_ip_address', args=(subnet_id,)),
            data=post_data,
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(str(IpAddress.objects.first().ip_address), '10.0.0.2')

    def test_read_ip_address_api(self):
        subnet = self._create_subnet(subnet='10.0.0.0/24')
        ip_address = self._create_ipaddress(ip_address='10.0.0.1', subnet=subnet)
        response = self.client.get(reverse('ipam:ip_address', args=(ip_address.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['ip_address'], '10.0.0.1')

    def test_update_ip_address_api(self):
        subnet = self._create_subnet(subnet='10.0.0.0/24')
        ip_address = self._create_ipaddress(ip_address='10.0.0.1', subnet=subnet)
        response = self.client.patch(
            reverse('ipam:ip_address', args=(ip_address.id,)),
            data=json.dumps({'description': 'Test Ip address'}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            IpAddress.objects.get(pk=ip_address.id).description, 'Test Ip address',
        )

    def test_delete_ip_address_api(self):
        subnet = self._create_subnet(subnet='10.0.0.0/24')
        ip_address = self._create_ipaddress(ip_address='10.0.0.1', subnet=subnet)
        response = self.client.delete(reverse('ipam:ip_address', args=(ip_address.id,)))
        self.assertEqual(response.status_code, 204)
        self.assertEqual(IpAddress.objects.count(), 0)

    def test_list_ipadress_subnet_api(self):
        subnet = self._create_subnet(subnet='10.0.0.0/24')
        self._create_ipaddress(ip_address='10.0.0.1', subnet=subnet)
        self._create_ipaddress(ip_address='10.0.0.2', subnet=subnet)
        response = self.client.get(
            reverse('ipam:list_create_ip_address', args=(subnet.id,)) + '?page=1'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['results'][0]['ip_address'], '10.0.0.1')
        self.assertEqual(response.data['results'][1]['ip_address'], '10.0.0.2')

    def test_export_subnet_api(self):
        subnet = self._create_subnet(subnet='10.0.0.0/24', name='Sample Subnet')
        self._create_ipaddress(
            ip_address='10.0.0.1', subnet=subnet, description='Testing'
        )
        self._create_ipaddress(
            ip_address='10.0.0.2', subnet=subnet, description='Testing'
        )
        csv_data = """Sample Subnet\r
        10.0.0.0/24\r
        \r
        ip_address,description\r
        10.0.0.1,Testing\r
        10.0.0.2,Testing\r
        """
        csv_data = bytes(csv_data.replace('        ', ''), 'utf-8')
        response = self.client.post(reverse('ipam:export-subnet', args=(subnet.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, csv_data)

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
        self.assertEqual(str(Subnet.objects.first().subnet), '10.27.1.0/24')
        self.assertEqual(str(IpAddress.objects.all()[0].ip_address), '10.27.1.1')
        self.assertEqual(str(IpAddress.objects.all()[1].ip_address), '10.27.1.254')

        csvfile = SimpleUploadedFile('data.txt', bytes(csv_data, 'utf-8'))
        response = self.client.post(
            reverse('ipam:import-subnet'), {'csvfile': csvfile}, follow=True
        )
        self.assertEqual(response.status_code, 400)
        csv_data = """Monachers - Matera,
        ,
        ,
        ip address,description
        10.27.1.1,Monachers
        10.27.1.254,Nano Beam 5 19AC"""
        invalid_file = SimpleUploadedFile('data.csv', bytes(csv_data, 'utf-8'))
        response = self.client.post(
            reverse('ipam:import-subnet'), {'csvfile': invalid_file}
        )
        self.assertEqual(response.status_code, 400)

    def test_hosts_list_api(self):
        subnet = self._create_subnet(subnet='10.0.0.0/16')
        self._create_ipaddress(ip_address='10.0.0.1', subnet=subnet)
        self._create_ipaddress(ip_address='10.0.0.3', subnet=subnet)
        response = self.client.get(reverse('ipam:hosts', args=(subnet.id,)))
        self.assertEqual(response.data['results'][0]['address'], '10.0.0.1')
        self.assertEqual(response.data['results'][0]['used'], True)
        self.assertEqual(response.data['results'][1]['address'], '10.0.0.2')
        self.assertEqual(response.data['results'][1]['used'], False)
        self.assertEqual(response.data['results'][2]['address'], '10.0.0.3')
        self.assertEqual(response.data['results'][2]['used'], True)
        self.assertIsNone(response.data['previous'])
        response = self.client.get(response.data['next'])
        self.assertEqual(response.data['results'][0]['address'], '10.0.1.1')
        self.assertEqual(self.client.get(response.data['previous']).status_code, 200)
        self.assertEqual(self.client.get(response.data['next']).status_code, 200)
        response = self.client.get(
            reverse('ipam:hosts', args=(subnet.id,)), {'start': '10.0.255.1'}
        )
        self.assertEqual(self.client.get(response.data['previous']).status_code, 200)
        self.assertIsNone(response.data['next'])

    def test_unauthorized_api_access(self):
        self.client.logout()
        subnet = self._create_subnet(subnet='10.0.0.0/24')
        ip_address = self._create_ipaddress(ip_address='10.0.0.1', subnet=subnet)

        response = self.client.get(
            reverse('ipam:list_create_ip_address', args=(subnet.id,))
        )
        self.assertEqual(response.status_code, 403)

        response = self.client.delete(reverse('ipam:subnet', args=(subnet.id,)))
        self.assertEqual(response.status_code, 403)

        response = self.client.delete(reverse('ipam:ip_address', args=(ip_address.id,)))
        self.assertEqual(response.status_code, 403)

        response = self.client.post(
            reverse('ipam:subnet_list_create'),
            data=json.dumps(
                {'subnet': 'fdb6:21b:a477::9f7/64', 'description': 'Test Subnet'}
            ),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 403)
