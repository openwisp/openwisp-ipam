import swapper

from django_ipam.api.generics import (
    BaseAvailableIpView, BaseExportSubnetView, BaseImportSubnetView, BaseIpAddressListCreateView,
    BaseIpAddressView, BaseRequestIPView, BaseSubnetListCreateView, BaseSubnetView,
)

IpAddress = swapper.load_model('django_ipam', 'IpAddress')
Subnet = swapper.load_model('django_ipam', 'Subnet')


class AvailableIpView(BaseAvailableIpView):
    """
    Get the next available IP address under a subnet
    """
    subnet_model = Subnet
    queryset = IpAddress.objects.none()


class RequestIPView(BaseRequestIPView):
    """
    Request and create a record for the next available IP address under a subnet
    """
    subnet_model = Subnet
    queryset = IpAddress.objects.none()


class SubnetIpAddressListCreateView(BaseIpAddressListCreateView):
    """
    List/Create IP addresses under a specific subnet
    """
    subnet_model = Subnet


class SubnetListCreateView(BaseSubnetListCreateView):
    """
    List/Create subnets
    """
    queryset = Subnet.objects.all()


class SubnetView(BaseSubnetView):
    """
    View for retrieving, updating or deleting a subnet instance.
    """
    queryset = Subnet.objects.all()


class IpAddressView(BaseIpAddressView):
    """
    View for retrieving, updating or deleting a IP address instance.
    """
    queryset = IpAddress.objects.all()


class ImportSubnetView(BaseImportSubnetView):
    """
    View for importing a subnet from csv/xls/xlsx file.
    """
    subnet_model = Subnet
    queryset = Subnet.objects.none()


class ExportSubnetView(BaseExportSubnetView):
    """
    View for exporting a subnet to a csv file.
    """
    subnet_model = Subnet
    queryset = Subnet.objects.none()


import_subnet = ImportSubnetView.as_view()
export_subnet = ExportSubnetView.as_view()
request_ip = RequestIPView.as_view()
subnet_list_create = SubnetListCreateView.as_view()
subnet = SubnetView.as_view()
ip_address = IpAddressView.as_view()
subnet_list_ipaddress = SubnetIpAddressListCreateView.as_view()
get_first_available_ip = AvailableIpView.as_view()
