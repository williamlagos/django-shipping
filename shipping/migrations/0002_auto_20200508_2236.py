# Generated by Django 3.0.5 on 2020-05-08 22:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shipping', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='deliverable',
            name='mail_code',
            field=models.CharField(default='', max_length=100),
        ),
        migrations.AlterField(
            model_name='deliverable',
            name='name',
            field=models.CharField(default='((', max_length=50),
        ),
        migrations.AlterField(
            model_name='deliverableproperty',
            name='sku',
            field=models.CharField(default='', max_length=20),
        ),
    ]