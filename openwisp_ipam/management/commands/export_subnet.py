import swapper

from django_ipam.management.commands import BaseExportSubnetCommand


class Command(BaseExportSubnetCommand):
    subnet_model = swapper.load_model('django_ipam', 'Subnet')
