# Generated by Django 3.0.5 on 2021-12-08 12:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0003_auto_20211207_1416'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('New', 'New'), ('Completed', 'Completed'), ('Accepted', 'Accepted'), ('Cancelled', 'Cancelled')], default='New', max_length=10),
        ),
    ]
