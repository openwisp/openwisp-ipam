from openwisp_users.api.permissions import IsOrganizationMember
from rest_framework.exceptions import PermissionDenied


class OrgPermissionMixin(object):
    def validate_permission(self, user, organization):
        if not (
            user.is_superuser
            or IsOrganizationMember.validate_membership(self, user, organization)
        ):
            raise PermissionDenied(IsOrganizationMember.message)
