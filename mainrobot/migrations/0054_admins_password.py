# Generated by Django 5.0.4 on 2024-07-23 19:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainrobot', '0053_inovices_kind_pay'),
    ]

    operations = [
        migrations.AddField(
            model_name='admins',
            name='password',
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
    ]
