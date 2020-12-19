from django.core.exceptions import ValidationError
from rest_framework.exceptions import NotFound


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
