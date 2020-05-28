from openwisp_ipam.admin import IpAddressAdmin, SubnetAdmin  # noqa

# Monkey Patching Subnet Admin to change the name of the
# app_label used. Change this value to your <app_label>.
SubnetAdmin.app_label = 'sample_ipam'
