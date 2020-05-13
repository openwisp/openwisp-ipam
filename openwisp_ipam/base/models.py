import csv
from io import StringIO
from ipaddress import ip_address, ip_network

import xlrd
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from openwisp_users.mixins import OrgMixin
from openwisp_users.models import Organization
from openwisp_utils.base import TimeStampedEditableModel
from swapper import get_model_name, load_model

from .fields import NetworkField


class CsvImportException(Exception):
    pass


class AbstractSubnet(OrgMixin, TimeStampedEditableModel):
    name = models.CharField(max_length=100, blank=True, db_index=True)
    subnet = NetworkField(
        db_index=True,
        help_text=_(
            'Subnet in CIDR notation, eg: "10.0.0.0/24" '
            'for IPv4 and "fdb6:21b:a477::9f7/64" for IPv6'
        ),
    )
    description = models.CharField(max_length=100, blank=True)
    master_subnet = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='child_subnet_set',
    )

    class Meta:
        abstract = True
        indexes = [models.Index(fields=['subnet'], name='subnet_idx')]

    def __str__(self):
        if self.name:
            return '{0} {1}'.format(self.name, str(self.subnet))
        else:
            return str(self.subnet)

    def clean(self):
        if not self.subnet:
            return
        allowed_master = None
        for subnet in load_model('openwisp_ipam', 'Subnet').objects.filter().values():
            if self.id == subnet['id']:
                continue
            if ip_network(self.subnet).overlaps(subnet['subnet']):
                if not self.master_subnet and not subnet['subnet'].subnet_of(
                    ip_network(self.subnet)
                ):
                    raise ValidationError(
                        {'subnet': _('Subnet overlaps with %s') % subnet['subnet']}
                    )
                if not allowed_master or subnet['subnet'].subnet_of(allowed_master):
                    allowed_master = subnet['subnet']

        if self.master_subnet:
            if not ip_network(self.subnet).subnet_of(
                ip_network(self.master_subnet.subnet)
            ):
                raise ValidationError({'master_subnet': _('Invalid master subnet')})
            if ip_network(
                self.master_subnet.subnet
            ) != allowed_master and not allowed_master.subnet_of(
                ip_network(self.subnet)
            ):
                raise ValidationError(
                    {'subnet': _('Subnet overlaps with %s') % allowed_master}
                )

    def get_next_available_ip(self):
        ipaddress_set = [ip.ip_address for ip in self.ipaddress_set.all()]
        for host in self.subnet.hosts():
            if str(host) not in ipaddress_set:
                return str(host)
        return None

    def request_ip(self, options=None):
        if options is None:
            options = {}
        ip = self.get_next_available_ip()
        if not ip:
            return None
        ip_address = load_model('openwisp_ipam', 'IpAddress')(
            ip_address=ip, subnet=self, organization=self.organization, **options
        )
        ip_address.full_clean()
        ip_address.save()
        return ip_address

    def _read_subnet_data(self, reader):
        subnet_model = load_model('openwisp_ipam', 'Subnet')
        subnet_name = next(reader)[0].strip()
        subnet_value = next(reader)[0].strip()
        subnet_org = self._get_or_create_org(next(reader)[0].strip())
        try:
            subnet = subnet_model.objects.get(
                subnet=subnet_value, organization=subnet_org
            )
        except ValidationError as e:
            raise CsvImportException(str(e))
        except subnet_model.DoesNotExist:
            try:
                subnet = subnet_model(
                    name=subnet_name, subnet=subnet_value, organization=subnet_org
                )
                subnet.full_clean()
                subnet.save()
            except ValidationError as e:
                raise CsvImportException(str(e))
        return subnet

    def _read_ipaddress_data(self, reader, subnet):
        ipaddress_model = load_model('openwisp_ipam', 'IpAddress')
        ipaddress_list = []
        for row in reader:
            if not ipaddress_model.objects.filter(
                subnet=subnet,
                ip_address=row[0].strip(),
                organization=subnet.organization,
            ).exists():
                instance = ipaddress_model(
                    subnet=subnet,
                    ip_address=row[0].strip(),
                    description=row[1].strip(),
                    organization=subnet.organization,
                )
                try:
                    instance.full_clean()
                except ValueError as e:
                    raise CsvImportException(str(e))
                ipaddress_list.append(instance)
        for ip in ipaddress_list:
            ip.save()

    def import_csv(self, file):
        if file.name.endswith(('.xls', '.xlsx')):
            book = xlrd.open_workbook(file_contents=file.read())
            sheet = book.sheet_by_index(0)
            row = []
            for row_num in range(sheet.nrows):
                row.append(sheet.row_values(row_num))
            reader = iter(row)
        else:
            reader = csv.reader(StringIO(file.read().decode('utf-8')), delimiter=',')
        subnet = self._read_subnet_data(reader)
        next(reader)
        next(reader)
        self._read_ipaddress_data(reader, subnet)

    def export_csv(self, subnet_id, writer):
        ipaddress_model = load_model('openwisp_ipam', 'IpAddress')
        subnet = load_model('openwisp_ipam', 'Subnet').objects.get(pk=subnet_id)
        writer.writerow([subnet.name])
        writer.writerow([subnet.subnet])
        writer.writerow('')
        fields = [
            ipaddress_model._meta.get_field('ip_address'),
            ipaddress_model._meta.get_field('description'),
        ]
        writer.writerow(field.name for field in fields)
        for obj in subnet.ipaddress_set.all():
            row = []
            for field in fields:
                row.append(str(getattr(obj, field.name)))
            writer.writerow(row)

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


class AbstractIpAddress(OrgMixin, TimeStampedEditableModel):
    subnet = models.ForeignKey(
        get_model_name('openwisp_ipam', 'Subnet'), on_delete=models.CASCADE
    )
    ip_address = models.GenericIPAddressField()
    description = models.CharField(max_length=100, blank=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.ip_address

    def clean(self):
        if not self.ip_address or not self.subnet_id:
            return
        if ip_address(self.ip_address) not in self.subnet.subnet:
            raise ValidationError(
                {'ip_address': _('IP address does not belong to the subnet')}
            )
        addresses = load_model('openwisp_ipam', 'IpAddress').objects.all().values()
        for ip in addresses:
            if self.id == ip['id']:
                continue
            if ip_address(self.ip_address) == ip_address(ip['ip_address']):
                raise ValidationError({'ip_address': _('IP address already used.')})
