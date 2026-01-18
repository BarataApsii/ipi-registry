from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shareholders', '0003_add_total_shares_to_shareholder'),
    ]

    operations = [
        migrations.AddField(
            model_name='director',
            name='position',
            field=models.CharField(default='Director', max_length=100),
            preserve_default=False,
        ),
    ]
