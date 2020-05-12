import csv
from collections import OrderedDict

import swapper
from django import forms
from django.contrib import messages
from django.contrib.admin import ModelAdmin
from django.db.models import TextField
from django.db.models.functions import Cast
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import path, re_path, reverse
from django.utils.translation import gettext_lazy as _
from openwisp_users.multitenancy import MultitenantAdminMixin
from openwisp_utils.admin import TimeReadonlyAdminMixin

from ..api.views import HostsSet
from .forms import IpAddressImportForm
from .models import CsvImportException

Subnet = swapper.load_model('openwisp_ipam', 'Subnet')
IpAddress = swapper.load_model('openwisp_ipam', 'IpAddress')


class AbstractSubnetAdmin(MultitenantAdminMixin, TimeReadonlyAdminMixin, ModelAdmin):
    change_form_template = 'admin/openwisp-ipam/subnet/change_form.html'
    change_list_template = 'admin/openwisp-ipam/subnet/change_list.html'
    app_name = 'openwisp_ipam'
    list_display = ('name', 'subnet', 'master_subnet', 'description')
    autocomplete_fields = ['master_subnet']
    search_fields = ['subnet', 'name']

    def change_view(self, request, object_id, form_url='', extra_context=None):
        instance = Subnet.objects.get(pk=object_id)
        ipaddress_add_url = 'admin:{0}_ipaddress_add'.format(self.app_name)
        ipaddress_change_url = 'admin:{0}_ipaddress_change'.format(self.app_name)
        subnet_change_url = 'admin:{0}_subnet_change'.format(self.app_name)
        if request.GET.get('_popup'):
            return super().change_view(request, object_id, form_url, extra_context)
        # Find root master_subnet for subnet tree
        instance_root = instance
        while instance_root.master_subnet:
            instance_root = Subnet.objects.get(
                subnet=instance_root.master_subnet.subnet
            )
        # Get instances for all subnets for root master_subnet
        instance_subnets = Subnet.objects.filter(subnet=instance_root.subnet).values(
            "master_subnet", "pk", "name", "subnet"
        )
        # Make subnet tree
        collection_depth = 0
        subnet_tree = [instance_subnets]
        while instance_subnets:
            instance_subnets = Subnet.objects.none()
            for slave_subnet in subnet_tree[collection_depth]:
                instance_subnets = instance_subnets | Subnet.objects.filter(
                    master_subnet=slave_subnet["pk"]
                ).values("master_subnet", "pk", "name", "subnet")
            subnet_tree.append(instance_subnets)
            collection_depth += 1

        used = instance.ipaddress_set.count()

        # Storing UUID corresponding to respective IP address in a dictionary
        ip_id_list = (
            IpAddress.objects.filter(subnet=instance)
            .annotate(str_id=Cast('id', output_field=TextField()))
            .values_list('ip_address', 'str_id')
        )

        # Converting UUIdField to String and then modifying to convert back to uuid form
        ip_id_list = OrderedDict(ip_id_list)
        ip_uuid = {}
        for ip_addr, Ip in ip_id_list.items():
            ip_uuid[ip_addr] = f'{Ip[0:8]}-{Ip[8:12]}-{Ip[12:16]}-{Ip[16:20]}-{Ip[20:]}'
        available = HostsSet(instance).count() - used
        labels = ['Used', 'Available']
        values = [used, available]
        extra_context = {
            'labels': labels,
            'values': values,
            'original': instance,
            'ip_uuid': ip_uuid,
            'ipaddress_add_url': ipaddress_add_url,
            'ipaddress_change_url': ipaddress_change_url,
            'subnet_change_url': subnet_change_url,
            'subnet_tree': subnet_tree,
        }
        return super().change_view(request, object_id, form_url, extra_context)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            re_path(
                r'^(?P<subnet_id>[^/]+)/export-subnet/',
                self.export_view,
                name='ipam_export_subnet',
            ),
            path('import-subnet/', self.import_view, name='ipam_import_subnet'),
        ]
        return custom_urls + urls

    def export_view(self, request, subnet_id):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="ip_address.csv"'
        writer = csv.writer(response)
        Subnet().export_csv(subnet_id, writer)
        return response

    def import_view(self, request):
        form = IpAddressImportForm()
        form_template = 'admin/openwisp-ipam/subnet/import.html'
        subnet_list_url = 'admin:{0}_subnet_changelist'.format(self.app_name)
        context = {
            'form': form,
            'subnet_list_url': subnet_list_url,
            'has_permission': True,
        }
        if request.method == 'POST':
            form = IpAddressImportForm(request.POST, request.FILES)
            context['form'] = form
            if form.is_valid():
                file = request.FILES['csvfile']
                if not file.name.endswith(('.csv', '.xls', '.xlsx')):
                    messages.error(request, _('File type not supported.'))
                    return render(request, form_template, context)
                try:
                    Subnet().import_csv(file)
                except CsvImportException as e:
                    messages.error(request, str(e))
                    return render(request, form_template, context)
                messages.success(request, _('Successfully imported data.'))
                return redirect('/admin/{0}/subnet'.format(self.app_name))
        return render(request, form_template, context)

    class Media:
        js = (
            'admin/js/jquery.init.js',
            'admin/js/SelectBox.js',
            'openwisp-ipam/js/subnet.js',
            'openwisp-ipam/js/minified/jstree.min.js',
            'openwisp-ipam/js/minified/plotly.min.js',
        )
        css = {
            'all': (
                'openwisp-ipam/css/admin.css',
                'openwisp-ipam/css/minified/jstree.min.css',
            )
        }


class IpAddressAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['subnet'].help_text = _(
            'Select a subnet and the first available IP address '
            'will be automatically suggested in the ip address field'
        )


class AbstractIpAddressAdmin(MultitenantAdminMixin, TimeReadonlyAdminMixin, ModelAdmin):
    form = IpAddressAdminForm
    change_form_template = 'admin/openwisp-ipam/ip_address/change_form.html'
    list_display = ('ip_address', 'subnet', 'description')
    list_filter = ('subnet',)
    search_fields = ['ip_address']
    autocomplete_fields = ['subnet']

    class Media:
        js = (
            'admin/js/jquery.init.js',
            'openwisp-ipam/js/ip-request.js',
        )

    def get_extra_context(self):
        url = reverse('ipam:get_next_available_ip', args=['0000'])
        return {'get_next_available_ip_url': url}

    def add_view(self, request, form_url='', extra_context=None):
        return super().add_view(request, form_url, self.get_extra_context())

    def change_view(self, request, object_id, form_url='', extra_context=None):
        return super().change_view(
            request, object_id, form_url, self.get_extra_context()
        )

    def response_add(self, request, *args, **kwargs):
        """
        Custom reponse to dismiss an add form popup for IP address.
        """
        response = super().response_add(request, *args, **kwargs)
        if request.POST.get('_popup'):
            return HttpResponse(
                f"""
               <script type='text/javascript'>
                  opener.dismissAddAnotherPopup(window, '{request.POST.get('ip_address')}');
               </script>
             """
            )
        return response

    def response_change(self, request, *args, **kwargs):
        """
        Custom reponse to dismiss a change form popup for IP address.
        """
        response = super().response_change(request, *args, **kwargs)
        if request.POST.get('_popup'):
            return HttpResponse(
                """
               <script type='text/javascript'>
                  opener.dismissAddAnotherPopup(window);
               </script>
             """
            )
        return response
