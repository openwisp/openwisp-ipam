from openwisp_users.mixins import OrgMixin
from swapper import swappable_setting

from django_ipam.base.models import AbstractIpAddress, AbstractSubnet


class Subnet(OrgMixin, AbstractSubnet):
    class Meta(AbstractSubnet.Meta):
        abstract = False
        swappable = swappable_setting('openwisp_ipam', 'Subnet')


class IpAddress(OrgMixin, AbstractIpAddress):
    class Meta(AbstractIpAddress.Meta):
        abstract = False
        swappable = swappable_setting('openwisp_ipam', 'IpAddress')
