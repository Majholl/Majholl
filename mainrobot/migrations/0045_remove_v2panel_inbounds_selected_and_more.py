# Generated by Django 5.0.4 on 2024-06-27 16:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainrobot', '0044_alter_products_panel_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='v2panel',
            name='inbounds_selected',
        ),
        migrations.AddField(
            model_name='products',
            name='inbounds_selected',
            field=models.JSONField(blank=True, default=None, null=True),
        ),
    ]
