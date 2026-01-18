from django.db import migrations, models
from django.conf import settings

class Migration(migrations.Migration):

    dependencies = [
        ('shareholders', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('transaction_type', models.CharField(choices=[('ISSUE', 'Share Issue'), ('TRANSFER', 'Transfer'), ('ADJUSTMENT', 'Adjustment')], max_length=20)),
                ('shares', models.IntegerField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('shareholder', models.ForeignKey(on_delete=models.CASCADE, related_name='transactions', to='shareholders.shareholder')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=models.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
