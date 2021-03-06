# Generated by Django 3.2.3 on 2021-06-02 06:26

from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_account'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='balance',
            field=models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=9),
        ),
        migrations.AddField(
            model_name='account',
            name='currency',
            field=models.CharField(choices=[('PEN', 'PEN'), ('USD', 'USD')], default='PEN', max_length=3),
        ),
        migrations.AddField(
            model_name='user',
            name='favorite_currency',
            field=models.CharField(choices=[('PEN', 'PEN'), ('USD', 'USD')], default='PEN', max_length=3),
        ),
    ]
