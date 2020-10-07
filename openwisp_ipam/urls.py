from django.conf.urls import url
from django.urls import include, path
from openwisp_users.api.urls import get_api_urls as get_users_api_urls

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
        url(r'^api/v1/', include((get_users_api_urls(), 'users'), namespace='users')),
    ]


urlpatterns = [path('', include(get_urls(ipam_api_views)))]
