from django.db import migrations

from openwisp_ipam.migrations import assign_permissions_to_groups


class Migration(migrations.Migration):
    dependencies = [
        ('sample_ipam', '0003_fix_multitenancy'),
    ]

    operations = [
        migrations.RunPython(
            assign_permissions_to_groups, reverse_code=migrations.RunPython.noop
        ),
    ]
