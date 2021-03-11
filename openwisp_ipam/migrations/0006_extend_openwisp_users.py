import django.db.models.deletion
from django.db import migrations, models
from swapper import get_model_name


class Migration(migrations.Migration):

    dependencies = [
        ('openwisp_ipam', '0005_default_groups_permissions'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subnet',
            name='organization',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to=get_model_name('openwisp_users', 'Organization'),
                verbose_name='organization',
            ),
        ),
    ]
