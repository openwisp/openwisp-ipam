from django_ipam.apps import DjangoIpamConfig


class OpenWispIpamConfig(DjangoIpamConfig):
    name = 'openwisp_ipam'
    verbose_name = 'IPAM'
