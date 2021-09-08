from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="home"),

    path('about', views.about, name="about"),

    path('service_maintenance', views.service_maintenance, name="service_maintenance"),
    path('service_remodel', views.service_remodel, name="service_remodel"),
    path('service_construction', views.service_construction, name="service_construction"),

    path('projects', views.projects, name="projects"),

    path('contact', views.contact, name="contact"),

    path('test', views.test, name="test"),

]
