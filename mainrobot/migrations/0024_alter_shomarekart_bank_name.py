# Generated by Django 5.0.7 on 2024-11-19 20:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainrobot', '0023_inovices_card_used'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shomarekart',
            name='bank_name',
            field=models.CharField(blank=True, max_length=124, null=True),
        ),
    ]
