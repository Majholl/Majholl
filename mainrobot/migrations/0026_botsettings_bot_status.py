# Generated by Django 5.0.4 on 2024-11-21 12:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainrobot', '0025_botsettings_notif_mode'),
    ]

    operations = [
        migrations.AddField(
            model_name='botsettings',
            name='bot_status',
            field=models.PositiveBigIntegerField(default=0, null=True),
        ),
    ]
