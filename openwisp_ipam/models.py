from openwisp_ipam.base.models import AbstractIpAddress, AbstractSubnet
from swapper import swappable_setting


class Subnet(AbstractSubnet):
    class Meta(AbstractSubnet.Meta):
        abstract = False
        swappable = swappable_setting('openwisp_ipam', 'Subnet')


class IpAddress(AbstractIpAddress):
    class Meta(AbstractIpAddress.Meta):
        abstract = False
        swappable = swappable_setting('openwisp_ipam', 'IpAddress')
