import json
import os

from openwisp_users.models import Organization

from django_ipam.tests import (
    CreateModelsMixin as BaseCreateModelsMixin, FileMixin as BaseFileMixin,
    PostDataMixin as BasePostDataMixin,
)


class FileMixin(BaseFileMixin):
    def _get_path(self, file):
        d = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(d, file)


class CreateModelsMixin(BaseCreateModelsMixin):
    def _create_org(self, **kwargs):
        options = dict(name='test-organization')
        options.update(kwargs)
        org = Organization(**options)
        org.save()
        return org

    def _get_extra_fields(self, **kwargs):
        org = Organization.objects.get_or_create(name='test-organization')
        options = dict(organization=org[0])
        return options


class PostDataMixin(BasePostDataMixin):
    def _post_data(self, **kwargs):
        org = Organization.objects.get_or_create(name='test-organization')
        kwargs['organization'] = str(org[0].pk)
        return json.dumps(dict(kwargs))
