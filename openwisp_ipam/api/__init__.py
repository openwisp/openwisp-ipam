from django.conf.urls import url


def get_api_urls(api_views):
    """
    returns:: all the API urls of the app
    arguements::
        api_views: location for getting API views
    """

    return [
        url(r'^import-subnet/$', api_views.import_subnet, name='import-subnet'),
        url(
            r'^subnet/(?P<subnet_id>[^/]+)/get-next-available-ip/$',
            api_views.get_next_available_ip,
            name='get_next_available_ip',
        ),
        url(
            r'^subnet/(?P<subnet_id>[^/]+)/request-ip/$',
            api_views.request_ip,
            name='request_ip',
        ),
        url(
            r'^subnet/(?P<subnet_id>[^/]+)/export/$',
            api_views.export_subnet,
            name='export-subnet',
        ),
        url(
            r'^subnet/(?P<subnet_id>[^/]+)/ip-address$',
            api_views.subnet_list_ipaddress,
            name='list_create_ip_address',
        ),
        url(r'^subnet/$', api_views.subnet_list_create, name='subnet_list_create'),
        url(r'^subnet/(?P<pk>[^/]+)$', api_views.subnet, name='subnet'),
        url(
            r'^subnet/(?P<subnet_id>[^/]+)/hosts$', api_views.subnet_hosts, name='hosts'
        ),
        url(r'^ip-address/(?P<pk>[^/]+)/$', api_views.ip_address, name='ip_address'),
    ]
