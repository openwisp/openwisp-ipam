from openwisp_users.multitenancy import MultitenantRelatedOrgFilter
from swapper import load_model

Subnet = load_model('openwisp_ipam', 'Subnet')


class SubnetFilter(MultitenantRelatedOrgFilter):
    field_name = 'subnet'
    parameter_name = 'subnet_id'


class SubnetOrganizationFilter(MultitenantRelatedOrgFilter):
    field_name = 'organization'
    parameter_name = 'subnet__organization'
    rel_model = Subnet
