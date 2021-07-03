# Generated by Django 3.2.3 on 2021-06-03 04:31

import core.models
from decimal import Decimal
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_auto_20210602_0626'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='type',
            field=models.CharField(choices=[('C', 'Checking Account'), ('S', 'Savings'), ('I', 'Investments'), ('W', 'Wallet')], max_length=1),
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=9)),
                ('date', models.DateField(default=core.models.Transaction.get_current_date)),
                ('type', models.CharField(choices=[('T', 'Transfer'), ('I', 'Income'), ('E', 'Expense')], max_length=1)),
                ('is_paid', models.BooleanField(default=False)),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transactions', to='core.account')),
            ],
        ),
    ]