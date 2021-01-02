import swapper
from django.contrib.auth.models import Permission
from django.core.exceptions import ValidationError
from rest_framework.exceptions import NotFound, PermissionDenied

Organization = swapper.load_model('openwisp_users', 'Organization')


class FilterByOrganization:
    def get_queryset(self):
        qs = super().get_queryset()
        # superuser has access to every organization
        if self.request.user.is_superuser:
            return qs
        # non superuser has access only to some organizations
        return self.get_organization_queryset(qs)

    def get_organization_queryset(self):
        raise NotImplementedError()


class FilterByOrganizationManaged(FilterByOrganization):
    """
    Allows to filter only organizations which the current user manages
    """

    def get_organization_queryset(self, qs):
        return qs.filter(organization__in=self.request.user.organizations_managed)


class FilterByParent:
    def get_queryset(self):
        qs = super().get_queryset()
        self.assert_parent_exists()
        return qs

    def assert_parent_exists(self):
        parent_queryset = self.get_parent_queryset()
        if not self.request.user.is_superuser:
            parent_queryset = self.get_organization_queryset(parent_queryset)
        try:
            assert parent_queryset.exists()
        except (AssertionError, ValidationError):
            raise NotFound(detail='No relevant data found.')

    def get_parent_queryset(self):
        raise NotImplementedError()

    def get_organization_queryset(self):
        raise NotImplementedError()


class FilterByParentManaged(FilterByParent):
    def get_organization_queryset(self, qs):
        return qs.filter(organization__in=self.request.user.organizations_managed)


class AuthorizeCSVImport:
    def post(self, request):
        self.assert_organization_permissions(request)

    def assert_organization_permissions(self, request):
        if request.user.is_superuser:
            return
        try:
            organization = self.get_csv_organization()
            if str(organization.pk) in self.get_user_organizations():
                return
        except Organization.DoesNotExist:
            # if organization in CSV doesn't exist, then check if
            # user can create new organizations
            permission = Permission.objects.filter(user=request.user).filter(
                codename='add_organization'
            )
            if permission.exists():
                return
        raise PermissionDenied()

    def get_csv_organization(self):
        raise NotImplementedError()

    def get_user_organizations(self):
        raise NotImplementedError()


class AuthorizeCSVOrgManaged(AuthorizeCSVImport):
    def get_user_organizations(self):
        return self.request.user.organizations_managed


class FilterSerializerByOrganization:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.context['request'].user.is_superuser:
            return
        self.filter_fields()

    def filter_fields(self):
        raise NotImplementedError()


class FilterSerializerByOrgManaged(FilterSerializerByOrganization):
    def filter_fields(self):
        user = self.context['request'].user
        organization_filter = user.organizations_managed
        for field in self.fields:
            if field == 'organization':
                self.fields[field].queryset = self.fields[field].queryset.filter(
                    pk__in=organization_filter
                )
            else:
                try:
                    self.fields[field].queryset = self.fields[field].queryset.filter(
                        organization__in=organization_filter
                    )
                except AttributeError:
                    pass
