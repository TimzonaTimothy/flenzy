# Generated by Django 3.0.5 on 2021-12-08 12:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0004_auto_20211208_1347'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('Cancelled', 'Cancelled'), ('New', 'New'), ('Completed', 'Completed'), ('Accepted', 'Accepted')], default='New', max_length=10),
        ),
    ]
