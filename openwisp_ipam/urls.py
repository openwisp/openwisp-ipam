from django.conf.urls import include, url

from .api import urls as api

app_name = 'ipam'
urlpatterns = [
    url(r'^api/v1/', include(api)),
]
