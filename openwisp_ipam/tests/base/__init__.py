import json
import os

from openwisp_users.models import Organization


class FileMixin(object):
    def _get_path(self, file):
        d = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(d, file)


class CreateModelsMixin(object):
    def _get_extra_fields(self, **kwargs):
        # For adding mandatory extra fields
        org = Organization.objects.get_or_create(name='test-organization')
        options = dict(organization=org[0])
        return options

    def _create_org(self, **kwargs):
        options = dict(name='test-organization')
        options.update(kwargs)
        org = Organization(**options)
        org.save()
        return org

    def _create_subnet(self, **kwargs):
        options = dict(subnet='', description='',)
        options.update(self._get_extra_fields())
        options.update(kwargs)
        instance = self.subnet_model(**options)
        instance.full_clean()
        instance.save()
        return instance

    def _create_ipaddress(self, **kwargs):
        options = dict(ip_address='', description='',)
        options.update(kwargs)
        instance = self.ipaddress_model(**options)
        instance.full_clean()
        instance.save()
        return instance


class PostDataMixin(object):
    def _post_data(self, **kwargs):
        org = Organization.objects.get_or_create(name='test-organization')
        kwargs['organization'] = str(org[0].pk)
        return json.dumps(dict(kwargs))
