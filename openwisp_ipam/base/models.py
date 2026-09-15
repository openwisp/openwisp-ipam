import csv
from bisect import bisect_right
from io import StringIO
from ipaddress import ip_address, ip_network

import openpyxl
from django.core.exceptions import ValidationError
from django.core.validators import validate_slug
from django.db import connections, models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from openwisp_users.mixins import ShareableOrgMixin
from openwisp_utils.base import TimeStampedEditableModel
from swapper import get_model_name, load_model

from .fields import NetworkField


class CsvImportException(Exception):
    pass


class AbstractSubnet(ShareableOrgMixin, TimeStampedEditableModel):
    name = models.CharField(max_length=100, db_index=True)
    subnet = NetworkField(
        db_index=True,
        help_text=_(
            'Subnet in CIDR notation, eg: "10.0.0.0/24" '
            'for IPv4 and "fdb6:21b:a477::9f7/64" for IPv6'
        ),
    )
    description = models.CharField(max_length=100, blank=True)
    master_subnet = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="child_subnet_set",
    )

    class Meta:
        abstract = True
        indexes = [models.Index(fields=["subnet"], name="subnet_idx")]
        unique_together = ("subnet", "organization")

    def __str__(self):
        return f"{self.name} {self.subnet}"

    def clean(self):
        if not self.subnet:
            return
        self._validate_multitenant_uniqueness()
        self._validate_multitenant_master_subnet()
        self._validate_multitenant_unique_child_subnet()
        self._validate_overlapping_subnets()
        self._validate_master_subnet_consistency()

    def _validate_multitenant_uniqueness(self):
        qs = self._meta.model.objects.exclude(pk=self.pk).filter(subnet=self.subnet)
        # find out if there's an identical subnet (shared)
        if qs.filter(organization=None).exists():
            raise ValidationError(
                {
                    "subnet": _(
                        "This subnet is already assigned for "
                        "internal usage in the system."
                    )
                }
            )
        # if adding a shared subnet, ensure the subnet
        # is not already taken by another org
        if not self.organization and qs.filter(organization__isnull=False).exists():
            raise ValidationError(
                {
                    "subnet": _(
                        "This subnet is already assigned to another organization."
                    )
                }
            )

    def _validate_multitenant_master_subnet(self):
        if not self.master_subnet:
            return
        if self.master_subnet.organization:
            self._validate_org_relation("master_subnet", field_error="master_subnet")

    def _validate_multitenant_unique_child_subnet(self):
        if self.master_subnet is None or self.master_subnet.organization_id is not None:
            return
        qs = self._meta.model.objects.exclude(id=self.pk).filter(subnet=self.subnet)
        if qs.exists():
            raise ValidationError(
                {
                    "subnet": _(
                        "This subnet is already assigned to another organization."
                    )
                }
            )

    def _validate_overlapping_subnets(self):
        organization_query = Q(organization_id=self.organization_id) | Q(
            organization_id__isnull=True
        )
        error_message = _("Subnet overlaps with {0}.")
        if (
            self.master_subnet and self.master_subnet.organization_id is None
        ) or self.organization is None:
            # The execution of above code implicitly ensures that
            # organization of both master_subnet and current subnet are
            # same. Otherwise, self._validate_multitenant_master_subnet
            # would have raised a validation error
            organization_query = Q()
            error_message = _("Subnet overlaps with a subnet of another organization.")

        qs = self._meta.model.objects.filter(organization_query).only("subnet")
        exclude = self.get_related_subnet_pks()
        # exclude also identical subnets (handled by other checks)
        qs = qs.exclude(pk__in=exclude).exclude(subnet=self.subnet)
        for subnet in qs.iterator():
            if ip_network(self.subnet).overlaps(subnet.subnet):
                raise ValidationError({"subnet": error_message.format(subnet.subnet)})

    def get_related_subnet_pks(self, organization_filter=None):
        """Return a list of primary keys for this subnet, its ancestors and descendants.

        The current subnet comes first, followed by its nearest ancestors and
        descendants level by level.
        """
        return (
            [self.pk]
            + self._get_parent_subnet_pks()
            + self.get_descendant_subnet_pks(organization_filter)
        )

    def _get_parent_subnet_pks(self):
        pks = []
        parent_subnet = self.master_subnet
        while parent_subnet:
            pks.append(parent_subnet.pk)
            parent_subnet = parent_subnet.master_subnet
        return pks

    def get_child_subnets(self, organization_filter=None):
        qs = self.child_subnet_set.all()
        if organization_filter is not None:
            qs = qs.filter(organization_filter)
        return qs

    def _get_containing_networks(self):
        networks = []
        subnet = self
        while subnet:
            networks.append(subnet.subnet)
            subnet = subnet.master_subnet
        return networks

    @staticmethod
    def _is_address_usable_in_network(address, network):
        """Check address usability within one network.

        IPv4 network and broadcast addresses are unusable except in ``/31``
        and ``/32`` networks. IPv6 network addresses are unusable except in
        ``/127`` and ``/128`` networks, while ``::`` and ``::1`` are always
        unusable.
        """
        if address.version != network.version or address not in network:
            return False
        if address.version == 6:
            if int(address) in (0, 1):
                return False
            return network.prefixlen >= 127 or address != network.network_address
        return network.prefixlen >= 31 or address not in (
            network.network_address,
            network.broadcast_address,
        )

    @classmethod
    def _is_ip_usable(cls, address, networks):
        return all(
            cls._is_address_usable_in_network(address, network) for network in networks
        )

    def is_ip_usable(self, address):
        """Check whether an IP address can be assigned to this subnet.

        The address must belong to this subnet and avoid unusable endpoints in
        this subnet and each ancestor subnet.
        """
        try:
            address = ip_address(address)
        except ValueError:
            return False
        return self._is_ip_usable(address, self._get_containing_networks())

    def get_available_subnets(self, prefixlen, *, ip_indexes=()):
        """Yield unused child subnets of the requested size, lowest first.

        This only finds candidates. It does not create or reserve subnet
        records. ``prefixlen`` is the CIDR prefix to use. ``ip_indexes`` lists
        zero-based addresses that will be assigned in each candidate. A
        candidate is skipped when any required address is unusable in it or one
        of its parent subnets.
        """
        subnet = self.subnet
        if not isinstance(prefixlen, int) or not (
            subnet.prefixlen < prefixlen <= subnet.max_prefixlen
        ):
            raise ValueError("prefixlen must be within the child subnet range")
        try:
            ip_indexes = tuple(ip_indexes)
        except TypeError as error:
            raise ValueError("ip_indexes must be an iterable of indexes") from error
        subnet_size = 1 << (subnet.max_prefixlen - prefixlen)
        if any(
            not isinstance(index, int)
            or isinstance(index, bool)
            or not 0 <= index < subnet_size
            for index in ip_indexes
        ):
            raise ValueError("ip_indexes must be valid indexes in the requested subnet")
        containing_networks = self._get_containing_networks()
        subnet_end = int(subnet.broadcast_address)
        candidate_start = int(subnet.network_address)
        occupied_ranges = sorted(
            (int(child.subnet.network_address), int(child.subnet.broadcast_address))
            for child in self.get_child_subnets().only("subnet").iterator()
        )
        for occupied_start, occupied_end in occupied_ranges:
            while candidate_start + subnet_size - 1 < occupied_start:
                candidate = ip_network(
                    (subnet._address_class(candidate_start), prefixlen)
                )
                if all(
                    self._is_ip_usable(
                        candidate[index], [candidate, *containing_networks]
                    )
                    for index in ip_indexes
                ):
                    yield candidate
                candidate_start += subnet_size
            if candidate_start <= occupied_end:
                candidate_start = ((occupied_end // subnet_size) + 1) * subnet_size
        while candidate_start + subnet_size - 1 <= subnet_end:
            candidate = ip_network((subnet._address_class(candidate_start), prefixlen))
            if all(
                self._is_ip_usable(candidate[index], [candidate, *containing_networks])
                for index in ip_indexes
            ):
                yield candidate
            candidate_start += subnet_size

    def get_descendant_subnet_pks(self, organization_filter=None, child_pks=None):
        """Return a list of primary keys for this subnet's descendants."""
        pks = []
        if child_pks is None:
            child_pks = list(
                self.get_child_subnets(organization_filter).values_list("pk", flat=True)
            )
        while child_pks:
            pks += child_pks
            qs = self._meta.model.objects.filter(master_subnet__in=child_pks)
            if organization_filter is not None:
                qs = qs.filter(organization_filter)
            child_pks = list(qs.values_list("pk", flat=True))
        return pks

    def _validate_master_subnet_consistency(self):
        if not self.master_subnet:
            return
        subnet_version = ip_network(self.subnet).version
        master_subnet_version = ip_network(self.master_subnet.subnet).version
        if subnet_version != master_subnet_version:
            raise ValidationError(
                {
                    "master_subnet": _(
                        f"IP version mismatch: Subnet {self.subnet} is IPv"
                        f"{subnet_version}, but Master Subnet "
                        f"{self.master_subnet.subnet} is IPv{master_subnet_version}."
                    )
                }
            )
        if not ip_network(self.subnet).subnet_of(ip_network(self.master_subnet.subnet)):
            raise ValidationError({"master_subnet": _("Invalid master subnet.")})

    def get_next_available_ip(self):
        """Return the next assignable, unallocated IP address in this subnet.

        Usability is checked against this subnet and its ancestors. Existing
        IP address records directly assigned to this subnet are skipped.
        """
        ipaddress_set = set(self.ipaddress_set.values_list("ip_address", flat=True))
        containing_networks = self._get_containing_networks()
        subnet_hosts = self.subnet.hosts()
        for host in subnet_hosts:
            if (
                self._is_ip_usable(host, containing_networks)
                and str(host) not in ipaddress_set
            ):
                return str(host)
        return None

    def get_allocation(self, organization_filter=None):
        """Return counts of total, used, reserved, and available addresses.

        Addresses with IP records in this subnet or its descendants are used.
        Remaining addresses in direct child subnets are reserved.
        """
        start, end = self._get_usable_address_range()
        reserved = 0
        reserved_ranges = []
        child_pks = []
        for child in (
            self.get_child_subnets(organization_filter)
            .only("subnet", "master_subnet")
            .iterator()
        ):
            child_pks.append(child.pk)
            child_start = max(start, int(child.subnet.network_address))
            child_end = min(end, int(child.subnet.broadcast_address))
            if child_start <= child_end:
                reserved += child_end - child_start + 1
                reserved_ranges.append((child_start, child_end))
        reserved_ranges.sort()
        total = max(end - start + 1, 0)
        descendant_pks = self.get_descendant_subnet_pks(organization_filter, child_pks)
        IpAddress = load_model("openwisp_ipam", "IpAddress")
        used_queryset = IpAddress.objects.filter(
            subnet_id__in=[self.pk] + self._get_parent_subnet_pks() + descendant_pks
        )
        used, reserved_used = self._get_used_counts(
            used_queryset,
            start,
            end,
            reserved_ranges,
        )
        if reserved_ranges:
            reserved = max(reserved - reserved_used, 0)
        return {
            "total": total,
            "used": used,
            "reserved": reserved,
            "available": max(total - used - reserved, 0),
        }

    @staticmethod
    def _get_used_counts(queryset, start, end, ranges):
        """Count used addresses and the used addresses inside child subnet ranges.

        `used` counts every IP address in the displayed subnet range. `reserved_used`
        counts only used addresses in direct child subnet ranges, so the caller can
        subtract them from `reserved`. Sorted, non-overlapping ranges allow binary
        search to perform that check efficiently.
        """
        # PostgreSQL stores GenericIPAddressField as inet, unlike text-backed SQLite.
        if connections[queryset.db].vendor == "postgresql":
            queryset = queryset.filter(
                ip_address__range=(str(ip_address(start)), str(ip_address(end)))
            )
        range_starts = [range_start for range_start, _ in ranges]
        used = 0
        reserved_used = 0
        for address in queryset.values_list("ip_address", flat=True).iterator():
            address = int(ip_address(address))
            if not start <= address <= end:
                continue
            used += 1
            range_index = bisect_right(range_starts, address) - 1
            if range_index >= 0 and address <= ranges[range_index][1]:
                reserved_used += 1
        return used, reserved_used

    def _get_usable_address_range(self):
        start = int(self.subnet.network_address)
        end = int(self.subnet.broadcast_address)
        networks = self._get_containing_networks()
        while start <= end and not self._is_ip_usable(
            self.subnet._address_class(start), networks
        ):
            start += 1
        while start <= end and not self._is_ip_usable(
            self.subnet._address_class(end), networks
        ):
            end -= 1
        return start, end

    def request_ip(self, options=None):
        """Create and return the next assignable IP address in this subnet.

        ``options`` are passed to the new IP address record. Returns ``None``
        when the subnet has no assignable, unallocated addresses.
        """
        if options is None:
            options = {}
        ip = self.get_next_available_ip()
        if not ip:
            return None
        ip_address = load_model("openwisp_ipam", "IpAddress")(
            ip_address=ip, subnet=self, **options
        )
        ip_address.full_clean()
        ip_address.save()
        return ip_address

    def _read_row(self, reader):
        value = next(reader)
        if len(value) > 0:
            return value[0].strip()
        return None

    def _read_subnet_data(self, reader):
        subnet_model = load_model("openwisp_ipam", "Subnet")
        subnet_name = self._read_row(reader)
        subnet_value = self._read_row(reader)
        org_slug = self._read_row(reader)
        subnet_org = self._get_org(org_slug)
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
        ipaddress_model = load_model("openwisp_ipam", "IpAddress")
        ipaddress_list = []
        for row in reader:
            description = str(row[1] or "").strip()
            if not ipaddress_model.objects.filter(
                subnet=subnet,
                ip_address=row[0].strip(),
            ).exists():
                instance = ipaddress_model(
                    subnet=subnet,
                    ip_address=row[0].strip(),
                    description=description,
                )
                try:
                    instance.full_clean()
                except ValueError as e:
                    raise CsvImportException(str(e))
                ipaddress_list.append(instance)
        for ip in ipaddress_list:
            ip.save()

    def _get_csv_reader(self, file):
        if file.name.endswith((".xlsx")):
            book = openpyxl.load_workbook(filename=file)
            sheet = book.worksheets[0]
            reader = sheet.values
        else:
            reader = csv.reader(StringIO(file.read().decode("utf-8")), delimiter=",")
        return reader

    def import_csv(self, file):
        reader = self._get_csv_reader(file)
        subnet = self._read_subnet_data(reader)
        next(reader)
        next(reader)
        self._read_ipaddress_data(reader, subnet)

    def export_csv(self, subnet_id, writer):
        ipaddress_model = load_model("openwisp_ipam", "IpAddress")
        subnet = load_model("openwisp_ipam", "Subnet").objects.get(pk=subnet_id)
        writer.writerow([subnet.name])
        writer.writerow([subnet.subnet])
        writer.writerow([subnet.organization.slug] if subnet.organization else "")
        writer.writerow("")
        fields = [
            ipaddress_model._meta.get_field("ip_address"),
            ipaddress_model._meta.get_field("description"),
        ]
        writer.writerow(field.name for field in fields)
        for obj in subnet.ipaddress_set.all():
            row = []
            for field in fields:
                row.append(str(getattr(obj, field.name)))
            writer.writerow(row)

    def _get_org(self, org_slug):
        Organization = load_model("openwisp_users", "Organization")
        if org_slug in [None, ""]:
            return None
        try:
            validate_slug(org_slug)
            instance = Organization.objects.get(slug=org_slug)
        except ValidationError as e:
            raise CsvImportException(str(e))
        except Organization.DoesNotExist:
            raise CsvImportException(
                "The import operation failed because the data being imported "
                f"belongs to an organization which is not recognized: “{org_slug}”. "
                "Please create this organization or adapt the CSV file being imported "
                "by pointing the data to another organization."
            )
        return instance


class AbstractIpAddress(TimeStampedEditableModel):
    subnet = models.ForeignKey(
        get_model_name("openwisp_ipam", "Subnet"), on_delete=models.CASCADE
    )
    ip_address = models.GenericIPAddressField()
    description = models.CharField(max_length=100, blank=True)

    class Meta:
        abstract = True
        verbose_name = _("IP address")
        verbose_name_plural = _("IP addresses")

    def __str__(self):
        return self.ip_address

    def clean(self):
        if not self.ip_address or not self.subnet_id:
            return
        if ip_address(self.ip_address) not in self.subnet.subnet:
            raise ValidationError(
                {"ip_address": _("IP address does not belong to the subnet")}
            )
        if not self.subnet.is_ip_usable(self.ip_address):
            raise ValidationError(
                {"ip_address": _("IP address is not usable in the subnet hierarchy.")}
            )
        self._validate_related_subnets()

    def _validate_related_subnets(self):
        subnet_pks = self.subnet.get_related_subnet_pks()
        duplicate = (
            load_model("openwisp_ipam", "IpAddress")
            .objects.filter(ip_address=self.ip_address, subnet_id__in=subnet_pks)
            .exclude(pk=self.pk)
            .exists()
        )
        if duplicate:
            raise ValidationError({"ip_address": _("IP address already used.")})
