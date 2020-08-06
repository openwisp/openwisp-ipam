"""
You don't need to have this file unless you plan
to modify the API views as well.
"""

import swapper

from openwisp_ipam.api.views import (
    AvailableIpView as BaseAvailableIpView,
    ExportSubnetView as BaseExportSubnetView,
    ImportSubnetView as BaseImportSubnetView,
    IpAddressListCreateView as BaseIpAddressListCreateView,
    IpAddressView as BaseIpAddressView,
    RequestIPView as BaseRequestIPView,
    SubnetHostsView as BaseSubnetHostsView,
    SubnetListCreateView as BaseSubnetListCreateView,
    SubnetView as BaseSubnetView,
)

IpAddress = swapper.load_model('openwisp_ipam', 'IpAddress')
Subnet = swapper.load_model('openwisp_ipam', 'Subnet')


class AvailableIpView(BaseAvailableIpView):
    """
    Get the next available IP address under a subnet
    """

    pass


class RequestIPView(BaseRequestIPView):
    """
    Request and create a record for the next available IP address under a subnet
    """

    pass


class IpAddressListCreateView(BaseIpAddressListCreateView):
    """
    List/Create IP addresses under a specific subnet
    """

    pass


class SubnetListCreateView(BaseSubnetListCreateView):
    """
    List/Create subnets
    """

    pass


class SubnetView(BaseSubnetView):
    """
    View for retrieving, updating or deleting a subnet instance.
    """

    pass


class IpAddressView(BaseIpAddressView):
    """
    View for retrieving, updating or deleting a IP address instance.
    """

    pass


class ImportSubnetView(BaseImportSubnetView):
    """
    View for importing a subnet from csv/xls/xlsx file.
    """

    pass


class ExportSubnetView(BaseExportSubnetView):
    """
    View for exporting a subnet to a csv file.
    """

    pass


class SubnetHostsView(BaseSubnetHostsView):
    """
    View for retrieving subnet's available/used hosts lists.
    """

    pass


import_subnet = ImportSubnetView.as_view()
export_subnet = ExportSubnetView.as_view()
request_ip = RequestIPView.as_view()
subnet_list_create = SubnetListCreateView.as_view()
subnet = SubnetView.as_view()
ip_address = IpAddressView.as_view()
subnet_list_ipaddress = IpAddressListCreateView.as_view()
get_next_available_ip = AvailableIpView.as_view()
subnet_hosts = SubnetHostsView.as_view()
