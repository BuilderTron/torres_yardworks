from django.db import models
from django.utils import timezone

from datetime import datetime, date


# Create your models here.


class HeroSlide (models.Model):
    title = models.CharField(max_length=200)
    image = models.ImageField(
        upload_to='images/homeslider', blank=True, null=True)
    description = models.TextField(blank=True)
    url = models.URLField(blank=True)
    # slug = models.SlugField(max_length=250, unique_for_date='publish')
    publish = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title


class Event (models.Model):
    title = models.CharField(max_length=200)
    # topLayer = models.CharField(max_length=200, blank=True)
    # logo = models.ImageField(upload_to='images/events/logos', blank=True, null=True)
    image = models.ImageField(upload_to='images/events', blank=True)
    description = models.TextField(blank=True)
    url = models.URLField(blank=True)
    # slug = models.SlugField(max_length=250, unique_for_date='publish')
    publish = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title



#Client Testimonies
class Testimonies(models.Model):
    name = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    testimony = models.TextField(max_length=400)
    profile = models.ImageField(upload_to='images/testimonies')

    def __str__(self):
        return self.name


# Gallery Section
##Categories
class GalleryCategorie(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name
##Image Upload
class GalleryUpload(models.Model):
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='images/gallery_page', blank=True)
    category = models.ForeignKey(GalleryCategorie, on_delete=models.CASCADE)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.title
    



# Contact Form Save 

class ClientLeads (models.Model):
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    email = models.EmailField(max_length=300)
    phone = models.CharField(max_length=20, blank=True)
    address = models.CharField(max_length=400, blank=True, null=True)
    date = models.CharField(max_length=12,blank=True, null=True)
    service = models.CharField(max_length=200, blank=True, null=True)
    subject = models.CharField(max_length=200, blank=True, null=True)
    message = models.TextField(max_length=600)

    def __str__(self):
        return self.first_name + ' ' + self.last_name

