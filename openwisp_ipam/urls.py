from django.urls import include, path

from .api import views as ipam_api_views
from .api.urls import get_api_urls


def get_urls(api_views=None):
    """
    returns:: all the urls of the openwisp-ipam module
    arguments::
        api_views: optional module or object providing custom API views,
                   any view not found in it falls back to the default one
    """
    return [
        path(
            "api/v1/ipam/", include((get_api_urls(api_views), "ipam"), namespace="ipam")
        ),
        path("accounts/", include("openwisp_users.accounts.urls")),
    ]


urlpatterns = [path("", include(get_urls(ipam_api_views)))]
