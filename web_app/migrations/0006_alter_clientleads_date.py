# Generated by Django 3.2.7 on 2021-10-07 22:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web_app', '0005_alter_clientleads_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='clientleads',
            name='date',
            field=models.CharField(blank=True, max_length=12, null=True),
        ),
    ]