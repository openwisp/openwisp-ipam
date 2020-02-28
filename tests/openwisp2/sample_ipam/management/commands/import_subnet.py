import swapper

from . import BaseImportSubnetCommand


class Command(BaseImportSubnetCommand):
    subnet_model = swapper.load_model('sample_ipam', 'Subnet')
