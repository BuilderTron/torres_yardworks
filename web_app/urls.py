from django.conf import settings
from django.urls import path
from . import views

urlpatterns = [
    path('health/', views.health_check, name="health_check"),
    path('', views.home, name="home"),

    path('about', views.about, name="about"),

    path('services', views.services, name="services"),
    path('lawn', views.lawn, name="lawn"),
    path('landscape', views.landscape, name="landscape"),
    path('outdoor', views.outdoor, name="outdoor"),
    path('indoor', views.indoor, name="indoor"),

    path('contact', views.contact, name="contact"),

    path('free_quote', views.free_quote, name="free_quote"),

    path('thank_you', views.thank_you, name="thank_you"),

    path('test', views.test, name="test"),
]

if settings.DEBUG:
    urlpatterns += [
        path('gallery', views.gallery, name="gallery"),
    ]
