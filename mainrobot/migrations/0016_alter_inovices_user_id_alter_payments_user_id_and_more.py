# Generated by Django 5.0.4 on 2024-10-15 00:03

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainrobot', '0015_alter_subscriptions_user_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inovices',
            name='user_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='mainrobot.users', to_field='user_id'),
        ),
        migrations.AlterField(
            model_name='payments',
            name='user_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='mainrobot.users', to_field='user_id'),
        ),
        migrations.AlterField(
            model_name='subscriptions',
            name='user_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='mainrobot.users', to_field='user_id'),
        ),
    ]
