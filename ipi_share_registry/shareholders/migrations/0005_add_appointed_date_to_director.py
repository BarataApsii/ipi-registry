from django.db import migrations, models
import datetime

class Migration(migrations.Migration):

    dependencies = [
        ('shareholders', '0004_add_position_to_director'),
    ]

    operations = [
        migrations.AddField(
            model_name='director',
            name='appointed_date',
            field=models.DateField(default=datetime.date.today),
            preserve_default=False,
        ),
    ]
