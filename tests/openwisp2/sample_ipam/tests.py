from openwisp_ipam.tests.test_admin import TestAdmin as BaseTestAdmin
from openwisp_ipam.tests.test_api import TestApi as BaseTestApi
from openwisp_ipam.tests.test_commands import TestCommands as BaseTestCommands
from openwisp_ipam.tests.test_forms import TestForms as BaseTestForms
from openwisp_ipam.tests.test_models import TestModels as BaseTestModels
from openwisp_ipam.tests.test_multitenant import (
    TestMultitenantAdmin as BaseTestMultitenantAdmin,
)


class TestAdmin(BaseTestAdmin):
    app_label = 'sample_ipam'


class TestApi(BaseTestApi):
    pass


class TestCommands(BaseTestCommands):
    pass


class TestForms(BaseTestForms):
    pass


class TestModels(BaseTestModels):
    pass


class TestMultitenantAdmin(BaseTestMultitenantAdmin):
    app_label = 'sample_ipam'


# this is necessary to avoid excuting the base test suites
del BaseTestAdmin
del BaseTestApi
del BaseTestCommands
del BaseTestForms
del BaseTestModels
del BaseTestMultitenantAdmin
