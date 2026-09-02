import csv
from collections import OrderedDict
from copy import deepcopy

import swapper
from django.db.models import Q
from django.http import HttpResponse
from django.utils.translation import gettext_lazy as _
from openwisp_users.api.mixins import (
    FilterByOrganizationManaged,
    FilterByParentManaged,
    ProtectedAPIMixin as BaseProtectedAPIMixin,
)
from openwisp_utils.api.pagination import OpenWispPagination
from rest_framework import pagination, serializers, status
from rest_framework.generics import (
    CreateAPIView,
    ListAPIView,
    ListCreateAPIView,
    RetrieveAPIView,
    RetrieveUpdateDestroyAPIView,
    get_object_or_404,
)
from rest_framework.response import Response
from rest_framework.utils.urls import remove_query_param, replace_query_param

from ..base.models import AbstractSubnet, CsvImportException
from .responses import HostsResponse
from .serializers import (
    HostsResponseSerializer,
    ImportSubnetSerializer,
    IpAddressSerializer,
    IpRequestSerializer,
    SubnetSerializer,
)
from .utils import AuthorizeCSVOrgManaged

IpAddress = swapper.load_model("openwisp_ipam", "IpAddress")
Subnet = swapper.load_model("openwisp_ipam", "Subnet")
Organization = swapper.load_model("openwisp_users", "Organization")


class IpAddressOrgMixin(FilterByParentManaged):
    def get_parent_queryset(self):
        qs = Subnet.objects.filter(pk=self.kwargs["subnet_id"])
        return qs

    def get_organization_filter(self):
        if self.request.user.is_superuser:
            return None
        organizations = self.request.user.organizations_managed
        conditions = Q(organization__in=organizations)
        if len(organizations):
            conditions |= Q(organization__isnull=True)
        return conditions

    def get_organization_queryset(self, qs):
        organization_filter = self.get_organization_filter()
        if organization_filter is not None:
            qs = qs.filter(organization_filter)
        return qs

    def get_subnet(self):
        qs = self.get_parent_queryset()
        if not self.request.user.is_superuser:
            qs = self.get_organization_queryset(qs)
        return get_object_or_404(qs)


class ProtectedAPIMixin(BaseProtectedAPIMixin):
    throttle_scope = "ipam"


class HostsListPagination(pagination.BasePagination):
    limit = 256
    start_query_param = "start"

    def paginate_queryset(self, queryset, request, view=None):
        self.count = queryset.count()
        self.queryset = queryset
        self.request = request
        self.offset = self.get_offset(request)
        return list(queryset[self.offset : self.offset + self.limit])  # noqa

    def get_paginated_response(self, data):
        return Response(
            OrderedDict(
                [
                    ("next", self.get_next_link()),
                    ("previous", self.get_previous_link()),
                    ("results", data),
                ]
            )
        )

    def get_offset(self, request):
        try:
            return self.queryset.index_of(request.query_params[self.start_query_param])
        except (KeyError, ValueError):
            return 0

    def get_next_link(self):
        if self.offset + self.limit >= self.count:
            return None
        url = self.request.build_absolute_uri()
        offset = self.offset + self.limit
        return replace_query_param(
            url, self.start_query_param, self.queryset[offset].address
        )

    def get_previous_link(self):
        if self.offset <= 0:
            return None
        url = self.request.build_absolute_uri()
        if self.offset - self.limit <= 0:
            return remove_query_param(url, self.start_query_param)
        offset = self.offset - self.limit
        return replace_query_param(
            url, self.start_query_param, self.queryset[offset].address
        )


class HostsSet:
    # Needed for DjangoModelPermissions to check the right model
    model = AbstractSubnet

    def __init__(self, subnet, start=0, stop=None, organization_filter=None):
        self.start = start
        self.stop = stop
        self.subnet = subnet
        self.organization_filter = organization_filter
        self.network = int(self.subnet.subnet.network_address)
        self.used_set = IpAddress.objects.filter(
            subnet_id__in=subnet.get_related_subnet_pks(organization_filter)
        )
        self.reserved_addresses = None

    def __getitem__(self, i):
        if isinstance(i, slice):
            start = i.start
            stop = i.stop
            if start is None:  # pragma: no cover
                start = 0
            if stop is None:  # pragma: no cover
                stop = self.count()
            else:
                stop = min(stop, self.count())
            return HostsSet(
                self.subnet,
                self.start + start,
                self.start + stop,
                organization_filter=self.organization_filter,
            )
        if i >= self.count():
            raise IndexError
        host = self._get_host(i)
        ip_address = self.used_set.filter(ip_address=str(host)).only("pk").first()
        return HostsResponse(
            str(host),
            ip_address=ip_address,
            reserved=self._is_reserved(host),
        )

    def _get_host(self, index):
        host = self.subnet.subnet._address_class(self.network + 1 + index + self.start)
        if self.subnet.subnet.prefixlen in [32, 128]:
            host = host - 1
        return host

    def _is_reserved(self, host):
        if self.stop is None:
            return any(
                host in child.subnet
                for child in self.subnet.get_child_subnets(self.organization_filter)
                .only("subnet", "master_subnet")
                .iterator()
            )
        if self.reserved_addresses is None:
            self.reserved_addresses = set()
            start = int(self._get_host(0))
            end = int(self._get_host(self.stop - self.start - 1))
            for child in (
                self.subnet.get_child_subnets(self.organization_filter)
                .only("subnet", "master_subnet")
                .iterator()
            ):
                child_start = max(start, int(child.subnet.network_address))
                child_end = min(end, int(child.subnet.broadcast_address))
                self.reserved_addresses.update(range(child_start, child_end + 1))
        return int(host) in self.reserved_addresses

    def count(self):
        if self.stop is not None:
            return self.stop - self.start
        broadcast = int(self.subnet.subnet.broadcast_address)
        # IPV4
        if self.subnet.subnet.version == 4:
            # Networks with a mask of 32 will return a list
            # containing the single host address
            if self.subnet.subnet.prefixlen == 32:
                return 1
            # Other than subnet /32, exclude broadcast
            return broadcast - self.network - 1
        # IPV6
        else:
            # Subnet/128 only contains single host address
            if self.subnet.subnet.prefixlen == 128:
                return 1
            return broadcast - self.network

    def __len__(self):
        return self.count()

    def index_of(self, address):
        index = int(self.subnet.subnet._address_class(address)) - self.network - 1
        if index < 0 or index >= self.count():  # pragma: no cover
            raise serializers.ValidationError({"detail": _("Invalid Address")})
        return index


class AvailableIpView(ProtectedAPIMixin, IpAddressOrgMixin, RetrieveAPIView):
    subnet_model = Subnet
    queryset = IpAddress.objects.none()
    serializer_class = serializers.Serializer

    def get(self, request, *args, **kwargs):
        subnet = get_object_or_404(self.subnet_model, pk=self.kwargs["subnet_id"])
        return Response(subnet.get_next_available_ip())


class IpAddressListCreateView(IpAddressOrgMixin, ProtectedAPIMixin, ListCreateAPIView):
    queryset = IpAddress.objects.none()
    subnet_model = Subnet
    serializer_class = IpAddressSerializer
    pagination_class = OpenWispPagination

    def get_queryset(self):
        subnet = get_object_or_404(self.subnet_model, pk=self.kwargs["subnet_id"])
        super().get_queryset()
        return subnet.ipaddress_set.all().order_by("ip_address")


class SubnetListCreateView(
    FilterByOrganizationManaged, ProtectedAPIMixin, ListCreateAPIView
):
    serializer_class = SubnetSerializer
    pagination_class = OpenWispPagination
    queryset = Subnet.objects.all().order_by("subnet")


class SubnetView(ProtectedAPIMixin, RetrieveUpdateDestroyAPIView):
    serializer_class = SubnetSerializer
    queryset = Subnet.objects.all()


class IpAddressView(ProtectedAPIMixin, RetrieveUpdateDestroyAPIView):
    serializer_class = IpAddressSerializer
    queryset = IpAddress.objects.all()
    organization_field = "subnet__organization"


class RequestIPView(ProtectedAPIMixin, IpAddressOrgMixin, CreateAPIView):
    subnet_model = Subnet
    queryset = IpAddress.objects.none()
    serializer_class = IpRequestSerializer

    def post(self, request, *args, **kwargs):
        options = {"description": request.data.get("description")}
        subnet = get_object_or_404(self.subnet_model, pk=kwargs["subnet_id"])
        ip_address = subnet.request_ip(options)
        if ip_address:
            serializer = IpAddressSerializer(
                ip_address, context={"request": self.request}
            )
            headers = self.get_success_headers(serializer.data)
            return Response(
                serializer.data, status=status.HTTP_201_CREATED, headers=headers
            )
        return Response(None)


class ImportSubnetView(ProtectedAPIMixin, CreateAPIView, AuthorizeCSVOrgManaged):
    subnet_model = Subnet
    queryset = Subnet.objects.none()
    serializer_class = ImportSubnetSerializer

    def get_csv_organization(self, request):
        data = self.subnet_model._get_csv_reader(
            self, deepcopy(request.FILES["csvfile"])
        )
        return self.subnet_model._get_org(self, org_slug=list(data)[2][0].strip())

    def post(self, request, *args, **kwargs):
        self.assert_organization_permissions(request)
        file = request.FILES["csvfile"]
        if not file.name.endswith((".csv", ".xls", ".xlsx")):
            return Response({"error": _("File type not supported.")}, status=400)
        try:
            self.subnet_model().import_csv(file)
        except CsvImportException as e:
            return Response({"error": _(str(e))}, status=400)
        return Response({"detail": _("Data imported successfully.")})


class ExportSubnetView(ProtectedAPIMixin, IpAddressOrgMixin, CreateAPIView):
    subnet_model = Subnet
    queryset = Subnet.objects.none()
    serializer_class = serializers.Serializer

    def post(self, request, *args, **kwargs):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="ip_address.csv"'
        writer = csv.writer(response)
        self.subnet_model().export_csv(kwargs["subnet_id"], writer)
        return response


class SubnetHostsView(IpAddressOrgMixin, ProtectedAPIMixin, ListAPIView):
    subnet_model = Subnet
    queryset = Subnet.objects.none()
    serializer_class = HostsResponseSerializer
    pagination_class = HostsListPagination

    def get_queryset(self):
        subnet = self.get_subnet()
        qs = HostsSet(subnet, organization_filter=self.get_organization_filter())
        return qs


class SubnetAllocationView(IpAddressOrgMixin, ProtectedAPIMixin, RetrieveAPIView):
    subnet_model = Subnet
    queryset = Subnet.objects.none()
    serializer_class = serializers.Serializer

    def get(self, request, *args, **kwargs):
        subnet = self.get_subnet()
        return Response(subnet.get_allocation(self.get_organization_filter()))


import_subnet = ImportSubnetView.as_view()
export_subnet = ExportSubnetView.as_view()
request_ip = RequestIPView.as_view()
subnet_list_create = SubnetListCreateView.as_view()
subnet = SubnetView.as_view()
ip_address = IpAddressView.as_view()
subnet_list_ipaddress = IpAddressListCreateView.as_view()
get_next_available_ip = AvailableIpView.as_view()
subnet_hosts = SubnetHostsView.as_view()
subnet_allocation = SubnetAllocationView.as_view()
