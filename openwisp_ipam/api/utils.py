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
