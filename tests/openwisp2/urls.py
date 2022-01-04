import os

from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from openwisp_users.api.urls import get_api_urls as get_users_api_urls

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('openwisp_utils.api.urls')),
    path('api/v1/', include((get_users_api_urls(), 'users'), namespace='users')),
]

if os.environ.get('SAMPLE_APP', False):
    # Load custom api views: This should be done when
    # you are extending the app and modifing the API
    # views in your extended application.
    from openwisp_ipam.urls import get_urls

    from .sample_ipam import views as api_views

    urlpatterns += [
        path('', include(get_urls(api_views))),
    ]
else:
    # Load openwisp_ipam api views: This can be used
    # when you are extending the app but not making
    # any changes in the API views.
    urlpatterns += [
        path('', include('openwisp_ipam.urls')),
        path('accounts/', include('openwisp_users.accounts.urls')),
    ]

if settings.DEBUG and 'debug_toolbar' in settings.INSTALLED_APPS:
    import debug_toolbar

    urlpatterns.append(path('__debug__/', include(debug_toolbar.urls)))
