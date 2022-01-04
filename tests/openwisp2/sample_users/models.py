from django.contrib.auth.models import Group as AbstractGroup
from django.core.validators import RegexValidator
from django.db import models
from openwisp_users.base.models import (
    AbstractUser,
    BaseGroup,
    BaseOrganization,
    BaseOrganizationOwner,
    BaseOrganizationUser,
)
from organizations.abstract import (
    AbstractOrganization,
    AbstractOrganizationInvitation,
    AbstractOrganizationOwner,
    AbstractOrganizationUser,
)


class User(AbstractUser):
    social_security_number = models.CharField(
        max_length=11,
        null=True,
        blank=True,
        validators=[RegexValidator(r'^\d\d\d-\d\d-\d\d\d\d$')],
    )

    class Meta(AbstractUser.Meta):
        abstract = False


class Organization(BaseOrganization, AbstractOrganization):
    pass


class OrganizationUser(BaseOrganizationUser, AbstractOrganizationUser):
    pass


class OrganizationOwner(BaseOrganizationOwner, AbstractOrganizationOwner):
    pass


# only needed for django-organizations~=2.x
class OrganizationInvitation(AbstractOrganizationInvitation):
    pass


class Group(BaseGroup, AbstractGroup):
    pass
