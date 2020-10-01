from django.urls import include, path

from .api import get_api_urls, views as ipam_api_views


def get_urls(api_views):
    """
    returns:: all the urls of the openwisp-ipam module
    arguements::
        api_views: location for getting API views
    """
    return [
        path('api/v1/', include((get_api_urls(api_views), 'ipam'), namespace='ipam')),
        path('accounts/', include('openwisp_users.accounts.urls')),
    ]


urlpatterns = [
    path('', include(get_urls(ipam_api_views))),
]
