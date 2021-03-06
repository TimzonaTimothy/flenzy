# Generated by Django 3.0.5 on 2021-12-16 19:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0006_auto_20211208_1355'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='payment',
            options={'ordering': ('-created_at',)},
        ),
        migrations.RenameField(
            model_name='payment',
            old_name='payment_id',
            new_name='ref',
        ),
        migrations.RemoveField(
            model_name='payment',
            name='payment_method',
        ),
        migrations.RemoveField(
            model_name='payment',
            name='status',
        ),
        migrations.AddField(
            model_name='payment',
            name='verified',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('Completed', 'Completed'), ('Accepted', 'Accepted'), ('Cancelled', 'Cancelled'), ('New', 'New')], default='New', max_length=10),
        ),
    ]
