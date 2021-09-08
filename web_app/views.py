from django.shortcuts import render
from django.core.mail import send_mail
from .models import HeroSlide, Event


# Home page.


def home(request):
    slide = HeroSlide.objects.all()
    event = Event.objects.all()
    return render(request, 'web_app/index.html', {'slides': slide, 'events': event})


def about(request):
    return render(request, 'web_app/about.html', {})


def service_maintenance(request):
    return render(request, 'web_app/service_maintenance.html', {})


def service_remodel(request):
    return render(request, 'web_app/service_remodel.html', {})


def service_construction(request):
    return render(request, 'web_app/service_construction.html', {})


def projects(request):
    return render(request, 'web_app/projects.html', {})


def contact(request):
    return render(request, 'web_app/contact.html', {})

# def contact(request):
#     if request.method == "POST":
#         your_name = request.POST['your_name']
#         email = request.POST['email']
#         message = request.POST['message']
# # Send Email
#         send_mail(
#             'NVP Web: ' + your_name,  # subject
#             message,  # messasge
#             email,  # from email
#             ['nvp20events@gmail.com'],  # to email
#             fail_silently=False,
#         )

#         return render(request, 'web_app/contact.html', {'your_name': your_name})

#     else:
#         return render(request, 'web_app/contact.html', {})


# Test page for models and forms
def test(request):

    return render(request, 'web_app/base.html', {})
