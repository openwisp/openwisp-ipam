from django.conf.urls import include, url

from .api import get_api_urls, views as ipam_api_views


def get_urls(api_views):
    """
    returns:: all the urls of the openwisp-ipam module
    arguements::
        api_views: location for getting API views
    """
    return [
        url(r'^api/v1/', include((get_api_urls(api_views), 'ipam'), namespace='ipam')),
        url(r'^accounts/', include('openwisp_users.accounts.urls')),
    ]


urlpatterns = [
    url(r'^', include(get_urls(ipam_api_views))),
]
