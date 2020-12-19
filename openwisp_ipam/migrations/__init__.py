from django.contrib.auth.management import create_permissions
from django.contrib.auth.models import Permission


def create_default_permissions(apps, schema_editor):
    for app_config in apps.get_app_configs():
        app_config.models_module = True
        create_permissions(app_config, apps=apps, verbosity=0)
        app_config.models_module = None


def assign_permissions_to_groups(apps, schema_editor):
    create_default_permissions(apps, schema_editor)
    admins_can_manage = ['subnet', 'ipaddress']
    operators_can_manage = ['ipaddress']
    manage_operations = ['add', 'change', 'delete', 'view']
    Group = apps.get_model('openwisp_users', 'Group')

    try:
        admin = Group.objects.get(name='Administrator')
        operator = Group.objects.get(name='Operator')
    except Group.DoesNotExist:
        return

    # Administrator - Can managae both ipaddress and subnet
    for model_name in admins_can_manage:
        for operation in manage_operations:
            permission = Permission.objects.get(
                codename='{}_{}'.format(operation, model_name)
            )
            admin.permissions.add(permission.pk)

    # Operator - Can manage ipaddress but can only `view` subnet
    for model_name in operators_can_manage:
        for operation in manage_operations:
            operator.permissions.add(
                Permission.objects.get(
                    codename='{}_{}'.format(operation, model_name)
                ).pk
            )

    try:
        permission = Permission.objects.get(codename='view_subnet')
        operator.permissions.add(permission.pk)
    except Permission.DoesNotExist:
        pass
