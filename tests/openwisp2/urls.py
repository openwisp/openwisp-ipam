import os

from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    url(r'^admin/', admin.site.urls),
]

if os.environ.get('SAMPLE_APP', False):
    # Load custom api views for sample app
    from openwisp_ipam.urls import get_urls
    from .sample_ipam import views as api_views

    urlpatterns += [
        url(r'^', include(get_urls(api_views))),
    ]
else:
    # Load openwisp_ipam api views
    urlpatterns += [
        url(r'^', include('openwisp_ipam.urls')),
    ]
