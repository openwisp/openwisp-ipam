from django.db import models

from openwisp_ipam.base.models import AbstractIpAddress, AbstractSubnet


class DetailsModel(models.Model):
    """
    This field serves no purpose, it only serves as an example
    for extending models and used for testing purposes.
    It will be inherited by all the models.
    """

    details = models.CharField(max_length=64, blank=True, null=True)

    class Meta:
        abstract = True


class IpAddress(DetailsModel, AbstractIpAddress):
    class Meta(AbstractIpAddress.Meta):
        abstract = False


class Subnet(DetailsModel, AbstractSubnet):
    class Meta(AbstractSubnet.Meta):
        abstract = False
