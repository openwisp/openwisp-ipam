from django.urls import path

from . import views


def get_api_urls(api_views=None):
    """
    returns:: all the API urls of the app
    arguments::
        api_views: optional module or object providing custom API views,
                   any view not found in it falls back to the default one
    """
    if api_views is None:
        api_views = views

    def get_view(name):
        """Fall back to the standard view when a custom view is unavailable."""
        return getattr(api_views, name, getattr(views, name))

    return [
        path("import-subnet/", get_view("import_subnet"), name="import-subnet"),
        path(
            "subnet/<str:subnet_id>/get-next-available-ip/",
            get_view("get_next_available_ip"),
            name="get_next_available_ip",
        ),
        path(
            "subnet/<str:subnet_id>/request-ip/",
            get_view("request_ip"),
            name="request_ip",
        ),
        path(
            "subnet/<str:subnet_id>/export/",
            get_view("export_subnet"),
            name="export-subnet",
        ),
        path(
            "subnet/<str:subnet_id>/ip-address/",
            get_view("subnet_list_ipaddress"),
            name="list_create_ip_address",
        ),
        path("subnet/", get_view("subnet_list_create"), name="subnet_list_create"),
        path("subnet/<str:pk>/", get_view("subnet"), name="subnet"),
        path("subnet/<str:subnet_id>/hosts/", get_view("subnet_hosts"), name="hosts"),
        path(
            "subnet/<str:subnet_id>/allocation/",
            get_view("subnet_allocation"),
            name="subnet_allocation",
        ),
        path("ip-address/<str:pk>/", get_view("ip_address"), name="ip_address"),
    ]
