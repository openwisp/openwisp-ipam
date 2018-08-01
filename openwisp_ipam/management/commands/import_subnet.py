import swapper

from django_ipam.management.commands import BaseImportSubnetCommand


class Command(BaseImportSubnetCommand):
    subnet_model = swapper.load_model('django_ipam', 'Subnet')
