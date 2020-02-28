import swapper
from django.contrib import admin
from openwisp_ipam.base.admin import AbstractIpAddressAdmin, AbstractSubnetAdmin

IpAddress = swapper.load_model("sample_ipam", "IpAddress")
Subnet = swapper.load_model("sample_ipam", "Subnet")


@admin.register(IpAddress)
class IPAddressAdmin(AbstractIpAddressAdmin):
    pass


@admin.register(Subnet)
class SubnetAdmin(AbstractSubnetAdmin):
    app_name = "sample_ipam"
