# Generated by Django 3.2.7 on 2021-10-08 13:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web_app', '0007_alter_clientleads_phone'),
    ]

    operations = [
        migrations.CreateModel(
            name='GalleryCategorie',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
            ],
        ),
    ]
