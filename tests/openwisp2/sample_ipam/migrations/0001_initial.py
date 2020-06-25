# Generated by Django 3.0.3 on 2020-04-08 14:28

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import model_utils.fields
import openwisp_ipam.base.fields
import openwisp_users.mixins
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('openwisp_users', '0007_unique_email'),
    ]

    operations = [
        migrations.CreateModel(
            name='Subnet',
            fields=[
                (
                    'id',
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    'created',
                    model_utils.fields.AutoCreatedField(
                        default=django.utils.timezone.now,
                        editable=False,
                        verbose_name='created',
                    ),
                ),
                (
                    'modified',
                    model_utils.fields.AutoLastModifiedField(
                        default=django.utils.timezone.now,
                        editable=False,
                        verbose_name='modified',
                    ),
                ),
                ('name', models.CharField(blank=True, db_index=True, max_length=100)),
                (
                    'subnet',
                    openwisp_ipam.base.fields.NetworkField(
                        db_index=True,
                        help_text='Subnet in CIDR notation, eg: "10.0.0.0/24" for IPv4 and "fdb6:21b:a477::9f7/64" for IPv6',
                        max_length=43,
                    ),
                ),
                ('description', models.CharField(blank=True, max_length=100)),
                ('details', models.CharField(blank=True, max_length=64, null=True)),
                (
                    'master_subnet',
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='child_subnet_set',
                        to='sample_ipam.Subnet',
                    ),
                ),
                (
                    'organization',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to='openwisp_users.Organization',
                        verbose_name='organization',
                    ),
                ),
            ],
            options={'abstract': False,},
            bases=(openwisp_users.mixins.ValidateOrgMixin, models.Model),
        ),
        migrations.CreateModel(
            name='IpAddress',
            fields=[
                (
                    'id',
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    'created',
                    model_utils.fields.AutoCreatedField(
                        default=django.utils.timezone.now,
                        editable=False,
                        verbose_name='created',
                    ),
                ),
                (
                    'modified',
                    model_utils.fields.AutoLastModifiedField(
                        default=django.utils.timezone.now,
                        editable=False,
                        verbose_name='modified',
                    ),
                ),
                ('ip_address', models.GenericIPAddressField()),
                ('description', models.CharField(blank=True, max_length=100)),
                ('details', models.CharField(blank=True, max_length=64, null=True)),
                (
                    'organization',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to='openwisp_users.Organization',
                        verbose_name='organization',
                    ),
                ),
                (
                    'subnet',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to='sample_ipam.Subnet',
                    ),
                ),
            ],
            options={'abstract': False,},
            bases=(openwisp_users.mixins.ValidateOrgMixin, models.Model),
        ),
        migrations.AddIndex(
            model_name='subnet',
            index=models.Index(fields=['subnet'], name='subnet_idx'),
        ),
    ]
