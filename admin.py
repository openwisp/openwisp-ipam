import csv
from ipaddress import IPv4Network, IPv6Network, ip_address

import swapper
from django import forms
from django.contrib import messages
from django.contrib.admin import ModelAdmin
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import path, re_path, reverse
from django.utils.translation import gettext_lazy as _
from openwisp_utils.admin import TimeReadonlyAdminMixin

from .forms import IpAddressImportForm
from .models import CsvImportException

Subnet = swapper.load_model('django_ipam', 'Subnet')
IpAddress = swapper.load_model('django_ipam', 'IpAddress')


class AbstractSubnetAdmin(TimeReadonlyAdminMixin, ModelAdmin):
    change_form_template = 'admin/django-ipam/subnet/change_form.html'
    change_list_template = 'admin/django-ipam/subnet/change_list.html'
    app_name = 'django_ipam'
    list_display = ('name', 'subnet', 'master_subnet', 'description')
    search_fields = ['subnet', 'name']

    def change_view(self, request, object_id, form_url='', extra_context=None):
        instance = Subnet.objects.get(pk=object_id)
        ipaddress_add_url = 'admin:{0}_ipaddress_add'.format(self.app_name)
        ipaddress_change_url = 'admin:{0}_ipaddress_change'.format(self.app_name)
        if request.GET.get('_popup'):
            return super(AbstractSubnetAdmin, self).change_view(request, object_id, form_url, extra_context)
        if type(instance.subnet) == IPv4Network:
            show_visual = True
            total = [host for host in instance.subnet.hosts()]
            used = len(list(instance.ipaddress_set.all()))
            used_ip = [ip_address(ip.ip_address) for ip in instance.ipaddress_set.all()]
            available = len(total) - used
            labels = ['Used', 'Available']
            values = [used, available]
            extra_context = {'labels': labels,
                             'values': values,
                             'total': total,
                             'subnet': instance,
                             'used_ip': used_ip,
                             'show_visual': show_visual,
                             'ipaddress_add_url': ipaddress_add_url,
                             'ipaddress_change_url': ipaddress_change_url}
        elif type(instance.subnet) == IPv6Network:
            used_ip = [ip for ip in instance.ipaddress_set.all()]
            used = len(used_ip)
            available = 2 ** (128 - instance.subnet.prefixlen) - used
            labels = ['Used', 'Available']
            values = [used, available]
            extra_context = {'labels': labels,
                             'values': values,
                             'used_ip': used_ip,
                             'subnet': instance,
                             'ipaddress_add_url': ipaddress_add_url,
                             'ipaddress_change_url': ipaddress_change_url}

        return super(AbstractSubnetAdmin, self).change_view(request, object_id, form_url, extra_context)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            re_path(r'^(?P<subnet_id>[^/]+)/export-subnet/',
                    self.export_view,
                    name='ipam_export_subnet'),
            path('import-subnet/', self.import_view, name='ipam_import_subnet'),
        ]
        return custom_urls + urls

    def export_view(self, request, subnet_id):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="ip_address.csv"'
        writer = csv.writer(response)
        Subnet.export_csv(self, subnet_id, writer)
        return response

    def import_view(self, request):
        form = IpAddressImportForm()
        form_template = 'admin/django-ipam/subnet/import.html'
        subnet_list_url = 'admin:{0}_subnet_changelist'.format(self.app_name)
        context = {
            'form': form,
            'subnet_list_url': subnet_list_url,
            'has_permission': True
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
                    Subnet.import_csv(self, file)
                except CsvImportException as e:
                    messages.error(request, str(e))
                    return render(request, form_template, context)
                messages.success(request, _('Successfully imported data.'))
                return redirect('/admin/{0}/subnet'.format(self.app_name))
        return render(request, form_template, context)

    class Media:
        js = ('django-ipam/js/custom.js',)
        css = {'all': ('django-ipam/css/admin.css',)}


class IpAddressAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(IpAddressAdminForm, self).__init__(*args, **kwargs)
        self.fields['subnet'].help_text = _('Select a subnet and the first available IP address '
                                            'will be automatically suggested in the ip address field')


class AbstractIpAddressAdmin(TimeReadonlyAdminMixin, ModelAdmin):
    form = IpAddressAdminForm
    change_form_template = 'admin/django-ipam/ip_address/change_form.html'
    list_display = ('ip_address', 'subnet', 'description')
    list_filter = ('subnet',)
    search_fields = ['ip_address']

    class Media:
        js = ('django-ipam/js/ip-request.js',)

    def get_extra_context(self):
        url = reverse('ipam:get_first_available_ip', args=['0000'])
        return {'get_first_available_ip_url': url}

    def add_view(self, request, form_url='', extra_context=None):
        return super(AbstractIpAddressAdmin, self).add_view(request, form_url, self.get_extra_context())

    def change_view(self, request, object_id, form_url='', extra_context=None):
        return super(AbstractIpAddressAdmin, self).change_view(request,
                                                               object_id,
                                                               form_url,
                                                               self.get_extra_context())

    def response_add(self, request, *args, **kwargs):
        """
        Custom reponse to dismiss an add form popup for IP address.
        """
        response = super(AbstractIpAddressAdmin, self).response_add(request, *args, **kwargs)
        if request.POST.get('_popup'):
            return HttpResponse("""
               <script type='text/javascript'>
                  opener.dismissAddAnotherPopup(window);
               </script>
             """)
        return response
