
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainrobot', '0019_rename_pro_id_products_pro_id_str'),
    ]

    operations = [
        migrations.AddField(
            model_name='v2panel',
            name='panel_status',
            field=models.SmallIntegerField(default=1),
        ),
    ]
