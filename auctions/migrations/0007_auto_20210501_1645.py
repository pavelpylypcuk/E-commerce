# Generated by Django 3.1.7 on 2021-05-01 14:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0006_auto_20210428_1654'),
    ]

    operations = [
        migrations.AlterField(
            model_name='auction_listing',
            name='description',
            field=models.CharField(max_length=150),
        ),
    ]
