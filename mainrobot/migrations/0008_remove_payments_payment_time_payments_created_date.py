# Generated by Django 5.0.4 on 2024-10-09 23:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainrobot', '0007_remove_inovices_user_username'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='payments',
            name='payment_time',
        ),
        migrations.AddField(
            model_name='payments',
            name='created_date',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]
