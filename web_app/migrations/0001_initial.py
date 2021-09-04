# Generated by Django 3.2.7 on 2021-09-03 23:02

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('image', models.ImageField(blank=True, upload_to='images/events')),
                ('description', models.TextField(blank=True)),
                ('url', models.URLField(blank=True)),
                ('publish', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='HeroSlide',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('image', models.ImageField(blank=True, null=True, upload_to='images/homeslider')),
                ('description', models.TextField(blank=True)),
                ('url', models.URLField(blank=True)),
                ('publish', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
    ]
