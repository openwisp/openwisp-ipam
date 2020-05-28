import os

from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    url(r'^admin/', admin.site.urls),
]

if os.environ.get('SAMPLE_APP', False):
    # Load custom api views: This should be done when
    # you are extending the app and modifing the API
    # views in your extended application.
    from openwisp_ipam.urls import get_urls
    from .sample_ipam import views as api_views

    urlpatterns += [
        url(r'^', include(get_urls(api_views))),
    ]
else:
    # Load openwisp_ipam api views: This can be used
    # when you are extending the app but not making
    # any changes in the API views.
    urlpatterns += [
        url(r'^', include('openwisp_ipam.urls')),
    ]
