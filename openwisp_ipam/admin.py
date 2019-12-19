from django.contrib import admin
from openwisp_users.multitenancy import MultitenantAdminMixin

from django_ipam.base.admin import AbstractIpAddressAdmin, AbstractSubnetAdmin

from .models import IpAddress, Subnet


@admin.register(IpAddress)
class IPAddressAdmin(MultitenantAdminMixin, AbstractIpAddressAdmin):
    pass


@admin.register(Subnet)
class BaseSubnet(MultitenantAdminMixin, AbstractSubnetAdmin):
    app_name = 'openwisp_ipam'
