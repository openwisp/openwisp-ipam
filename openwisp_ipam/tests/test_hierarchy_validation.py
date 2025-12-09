from django.test import TestCase
from django.core.exceptions import ValidationError
from openwisp_ipam.models import Subnet, IpAddress

class HierarchyTest(TestCase):
    def test_hierarchy_duplicate(self):
        parent = Subnet.objects.create(name='parent',subnet ="10.0.0.0/16")
        child = Subnet.objects.create(name='child',subnet="10.0.1.0/24")

        IpAddress.objects.create(ip_address="10.0.1.10", subnet=child)

        with self.assertRaises(ValidationError):
            obj=IpAddress(ip_address="10.0.1.10", subnet=parent)
            obj.full_clean()
            obj.save()