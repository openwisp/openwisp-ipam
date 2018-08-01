from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^import-subnet/$',
        views.import_subnet,
        name='import-subnet'),
    url(r'^subnet/(?P<subnet_id>[^/]+)/get-first-available-ip/$',
        views.get_first_available_ip,
        name='get_first_available_ip'),
    url(r'^subnet/(?P<subnet_id>[^/]+)/request-ip/$',
        views.request_ip,
        name='request_ip'),
    url(r'^subnet/(?P<subnet_id>[^/]+)/export/$',
        views.export_subnet,
        name='export-subnet'),
    url(r'^subnet/(?P<subnet_id>[^/]+)/ip-address$',
        views.subnet_list_ipaddress,
        name='list_create_ip_address'),
    url(r'^subnet/$',
        views.subnet_list_create,
        name='subnet_list_create'),
    url(r'^subnet/(?P<pk>[^/]+)$',
        views.subnet,
        name='subnet'),
    url(r'^ip-address/(?P<pk>[^/]+)/$',
        views.ip_address,
        name='ip_address'),
]
