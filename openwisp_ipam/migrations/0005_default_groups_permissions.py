from django.conf import settings
from django.db import migrations

from openwisp_ipam.migrations import assign_permissions_to_groups


class Migration(migrations.Migration):

    dependencies = [
        ('openwisp_users', '0011_user_first_name_150_max_length'),
        ('openwisp_ipam', '0004_subnet_organization_unique_together'),
    ]

    operations = [
        migrations.RunPython(
            assign_permissions_to_groups, reverse_code=migrations.RunPython.noop
        ),
    ]
