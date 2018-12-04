from django.core.exceptions import ValidationError
from openwisp_users.mixins import OrgMixin
from openwisp_users.models import Organization
from swapper import load_model, swappable_setting

from django_ipam.base.models import AbstractIpAddress, AbstractSubnet, CsvImportException


class Subnet(OrgMixin, AbstractSubnet):
    class Meta(AbstractSubnet.Meta):
        abstract = False
        swappable = swappable_setting('openwisp_ipam', 'Subnet')

    def request_ip(self, options=None):
        if options is None:
            options = {}
        ip = self.get_first_available_ip()
        if not ip:
            return None
        ip_address = load_model('openwisp_ipam',
                                'IpAddress')(ip_address=ip,
                                             subnet=self,
                                             organization=self.organization,
                                             **options)
        ip_address.full_clean()
        ip_address.save()
        return ip_address

    def _get_or_create_org(self, org_name):
        try:
            instance = Organization.objects.get(name=org_name)
        except ValidationError as e:
            raise CsvImportException(str(e))
        except Organization.DoesNotExist:
            try:
                instance = Organization(name=org_name)
                instance.save()
            except ValidationError as e:
                raise CsvImportException(str(e))
        return instance

    def _read_subnet_data(self, reader):
        subnet_model = load_model('openwisp_ipam', 'Subnet')
        subnet_name = next(reader)[0].strip()
        subnet_value = next(reader)[0].strip()
        subnet_org = self._get_or_create_org(next(reader)[0].strip())
        try:
            subnet = subnet_model.objects.get(subnet=subnet_value,
                                              organization=subnet_org)
        except ValidationError as e:
            raise CsvImportException(str(e))
        except subnet_model.DoesNotExist:
            try:
                subnet = subnet_model(name=subnet_name,
                                      subnet=subnet_value,
                                      organization=subnet_org)
                subnet.full_clean()
                subnet.save()
            except ValidationError as e:
                raise CsvImportException(str(e))
        return subnet

    def _read_ipaddress_data(self, reader, subnet):
        ipaddress_model = load_model('openwisp_ipam', 'IpAddress')
        ipaddress_list = []
        for row in reader:
            if not ipaddress_model.objects.filter(subnet=subnet,
                                                  ip_address=row[0].strip(),
                                                  organization=subnet.organization).exists():
                instance = ipaddress_model(subnet=subnet,
                                           ip_address=row[0].strip(),
                                           description=row[1].strip(),
                                           organization=subnet.organization)
                try:
                    instance.full_clean()
                except ValueError as e:
                    raise CsvImportException(str(e))
                ipaddress_list.append(instance)
        for ip in ipaddress_list:
            ip.save()


class IpAddress(OrgMixin, AbstractIpAddress):
    class Meta(AbstractIpAddress.Meta):
        abstract = False
        swappable = swappable_setting('openwisp_ipam', 'IpAddress')
