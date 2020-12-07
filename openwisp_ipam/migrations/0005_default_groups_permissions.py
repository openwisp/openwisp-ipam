from django.db import migrations

from openwisp_ipam.migrations import assign_permissions_to_groups


class Migration(migrations.Migration):

    dependencies = [
        ('openwisp_users', '0004_default_groups'),
        ('openwisp_ipam', '0004_subnet_organization_unique_together'),
    ]

    operations = [
        migrations.RunPython(
            assign_permissions_to_groups, reverse_code=migrations.RunPython.noop
        ),
    ]
