from django.conf.urls import include, url
from openwisp_utils.admin_theme.admin import admin, openwisp_admin

openwisp_admin()
admin.autodiscover()

urlpatterns = [
    url(r'^', include('openwisp_ipam.urls', namespace='ipam')),
    url(r'^admin/', admin.site.urls),
    url(r'^accounts/', include('allauth.urls')),
]
