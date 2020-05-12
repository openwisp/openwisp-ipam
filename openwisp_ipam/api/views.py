import csv
from collections import OrderedDict

import swapper
from django.http import HttpResponse
from django.utils.translation import gettext_lazy as _
from rest_framework import pagination, serializers, status
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.generics import (
    CreateAPIView, ListAPIView, ListCreateAPIView, RetrieveAPIView, RetrieveUpdateDestroyAPIView,
    get_object_or_404,
)
from rest_framework.permissions import DjangoModelPermissions
from rest_framework.response import Response
from rest_framework.utils.urls import remove_query_param, replace_query_param

from ..base.models import AbstractSubnet, CsvImportException
from .responses import HostsResponse
from .serializers import (
    HostsResponseSerializer, ImportSubnetSerializer, IpAddressSerializer, IpRequestSerializer,
    SubnetSerializer,
)

IpAddress = swapper.load_model('openwisp_ipam', 'IpAddress')
Subnet = swapper.load_model('openwisp_ipam', 'Subnet')


class ListViewPagination(pagination.PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class HostsListPagination(pagination.BasePagination):
    limit = 256
    start_query_param = 'start'

    def paginate_queryset(self, queryset, request, view=None):
        self.count = queryset.count()
        self.queryset = queryset
        self.request = request
        self.offset = self.get_offset(request)
        return list(queryset[self.offset: self.offset + self.limit])

    def get_paginated_response(self, data):
        return Response(
            OrderedDict(
                [
                    ('next', self.get_next_link()),
                    ('previous', self.get_previous_link()),
                    ('results', data),
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

    def __init__(self, subnet, start=0, stop=None):
        self.start = start
        self.stop = stop
        self.subnet = subnet
        self.network = int(self.subnet.subnet.network_address)
        self.used_set = subnet.ipaddress_set.all()

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
            return HostsSet(self.subnet, self.start + start, self.start + stop)
        if i >= self.count():
            raise IndexError
        host = self.subnet.subnet._address_class(self.network + 1 + i + self.start)
        used = self.used_set.filter(ip_address=str(host)).exists()
        return HostsResponse(str(host), used)

    def count(self):
        if self.stop is not None:
            return self.stop - self.start
        broadcast = int(self.subnet.subnet.broadcast_address)
        # IPV4 (exclude broadcast)
        if self.subnet.subnet.max_prefixlen == 32:
            return broadcast - self.network - 1
        # IPV6
        else:
            return broadcast - self.network

    def __len__(self):
        return self.count()

    def index_of(self, address):
        index = int(self.subnet.subnet._address_class(address)) - self.network - 1
        if index < 0 or index >= self.count():  # pragma: no cover
            raise IndexError
        return index


class AvailableIpView(RetrieveAPIView):
    subnet_model = Subnet
    queryset = IpAddress.objects.none()
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (DjangoModelPermissions,)

    def get(self, request, *args, **kwargs):
        subnet = get_object_or_404(self.subnet_model, pk=self.kwargs['subnet_id'])
        return Response(subnet.get_next_available_ip())


class IpAddressListCreateView(ListCreateAPIView):
    subnet_model = Subnet
    serializer_class = IpAddressSerializer
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (DjangoModelPermissions,)
    pagination_class = ListViewPagination

    def get_queryset(self):
        subnet = get_object_or_404(self.subnet_model, pk=self.kwargs['subnet_id'])
        return subnet.ipaddress_set.all().order_by('ip_address')


class SubnetListCreateView(ListCreateAPIView):
    serializer_class = SubnetSerializer
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (DjangoModelPermissions,)
    pagination_class = ListViewPagination
    queryset = Subnet.objects.all()


class SubnetView(RetrieveUpdateDestroyAPIView):
    serializer_class = SubnetSerializer
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (DjangoModelPermissions,)
    queryset = Subnet.objects.all()


class IpAddressView(RetrieveUpdateDestroyAPIView):
    serializer_class = IpAddressSerializer
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (DjangoModelPermissions,)
    queryset = IpAddress.objects.all()


class RequestIPView(CreateAPIView):
    subnet_model = Subnet
    queryset = IpAddress.objects.none()
    serializer_class = IpRequestSerializer
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (DjangoModelPermissions,)

    def post(self, request, *args, **kwargs):
        options = {'description': request.data.get('description')}
        subnet = get_object_or_404(self.subnet_model, pk=kwargs['subnet_id'])
        ip_address = subnet.request_ip(options)
        if ip_address:
            serializer = IpAddressSerializer(ip_address)
            headers = self.get_success_headers(serializer.data)
            return Response(
                serializer.data, status=status.HTTP_201_CREATED, headers=headers
            )
        return Response(None)


class ImportSubnetView(CreateAPIView):
    subnet_model = Subnet
    queryset = Subnet.objects.none()
    serializer_class = ImportSubnetSerializer
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (DjangoModelPermissions,)

    def post(self, request, *args, **kwargs):
        file = request.FILES['csvfile']
        if not file.name.endswith(('.csv', '.xls', '.xlsx')):
            return Response({'error': _('File type not supported.')}, status=400)
        try:
            self.subnet_model().import_csv(file)
        except CsvImportException as e:
            return Response({'error': _(str(e))}, status=400)
        return Response({'detail': _('Data imported successfully.')})


class ExportSubnetView(CreateAPIView):
    subnet_model = Subnet
    queryset = Subnet.objects.none()
    serializer_class = serializers.Serializer
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (DjangoModelPermissions,)

    def post(self, request, *args, **kwargs):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="ip_address.csv"'
        writer = csv.writer(response)
        self.subnet_model().export_csv(kwargs['subnet_id'], writer)
        return response


class SubnetHostsView(ListAPIView):
    subnet_model = Subnet
    queryset = Subnet.objects.none()
    serializer_class = HostsResponseSerializer
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (DjangoModelPermissions,)
    pagination_class = HostsListPagination

    def get_queryset(self):
        subnet = get_object_or_404(self.subnet_model, pk=self.kwargs['subnet_id'])
        qs = HostsSet(subnet)
        return qs


import_subnet = ImportSubnetView.as_view()
export_subnet = ExportSubnetView.as_view()
request_ip = RequestIPView.as_view()
subnet_list_create = SubnetListCreateView.as_view()
subnet = SubnetView.as_view()
ip_address = IpAddressView.as_view()
subnet_list_ipaddress = IpAddressListCreateView.as_view()
get_next_available_ip = AvailableIpView.as_view()
subnet_hosts = SubnetHostsView.as_view()
