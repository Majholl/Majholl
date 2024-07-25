# Generated by Django 5.0.4 on 2024-07-15 23:42

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainrobot', '0050_remove_v2panel_remain_capcity'),
    ]

    operations = [
        migrations.CreateModel(
            name='subscriptions',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_subscription', models.CharField(max_length=56)),
                ('panel_id', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='mainrobot.v2panel')),
                ('product_id', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='mainrobot.products')),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='mainrobot.users', to_field='user_id')),
            ],
            options={
                'db_table': 'TeleBot_subscriptions',
            },
        ),
    ]
