# Generated by Django 3.0.5 on 2021-12-08 12:55

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('store', '0007_auto_20211208_1354'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Review',
            new_name='ReviewRating',
        ),
        migrations.AlterField(
            model_name='variation',
            name='variation_category',
            field=models.CharField(choices=[('color', 'color'), ('size', 'size')], max_length=100),
        ),
    ]
