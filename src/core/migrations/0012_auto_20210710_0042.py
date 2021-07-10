# Generated by Django 3.2.5 on 2021-07-10 00:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_category'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='category',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='transactions', to='core.category'),
        ),
        migrations.AddField(
            model_name='transaction',
            name='logic_type',
            field=models.CharField(choices=[('I', 'Income'), ('E', 'Expense')], default='I', max_length=1),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='transaction',
            name='type',
            field=models.CharField(choices=[('T', 'Transfer'), ('I', 'Income'), ('E', 'Expense')], max_length=1),
        ),
    ]