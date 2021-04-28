import swapper
from django.contrib.auth.models import Permission
from rest_framework.exceptions import PermissionDenied

Organization = swapper.load_model('openwisp_users', 'Organization')


class AuthorizeCSVImport:
    def assert_organization_permissions(self, request):
        if request.user.is_superuser:
            return
        try:
            organization = self.get_csv_organization(request)
            if str(organization.pk) in self.get_user_organizations(request):
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
    def get_user_organizations(self, request):
        return request.user.organizations_managed
