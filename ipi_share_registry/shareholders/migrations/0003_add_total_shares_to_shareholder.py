from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shareholders', '0002_add_transaction_model'),
    ]

    operations = [
        migrations.AddField(
            model_name='shareholder',
            name='total_shares',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
