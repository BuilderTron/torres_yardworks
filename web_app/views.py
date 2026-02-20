from django.db import connection
from django.http import JsonResponse
from django.shortcuts import render
from django.core.mail import send_mail
from .models import HeroSlide, Event, ClientLeads, GalleryUpload, Testimonies


def health_check(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
    return JsonResponse({"status": "ok"})



# Home page.


def home(request):
    slide = HeroSlide.objects.all()
    event = Event.objects.all()
    testimony = Testimonies.objects.all()
    if request.method=="POST":
        first_name = request.POST['name']
        email = request.POST['email']
        phone = request.POST['phone']
        service = request.POST['service']
        message = request.POST['message']
        ins = ClientLeads(first_name=first_name,email=email,phone=phone,service=service,message=message)
        ins.save()

        msg_mail = "Name: " + str(first_name) + "\n\nEmail: " + str(email) + "\n\nPhone: " + str(phone) + "\n\nService: " + str(service) + "\n\nMessage: " + str(message)
        # Send Email
        send_mail(
            'Torres Small Request Form by: ' + first_name,  # subject
            msg_mail,
            email,
            ['torresyardworks@gmail.com'],  # to email
            fail_silently=False,
        )
        print("Data has been written in db.")
        return render(request, 'web_app/thank_you.html', {'first_name': first_name})
    else:
        return render(request, 'web_app/index.html', {'slides': slide, 'events': event, 'testimonys': testimony})



def about(request):
    return render(request, 'web_app/about.html', {})


def services(request):
    return render(request, 'web_app/services.html', {})


def lawn(request):
    return render(request, 'web_app/lawn_gardencare.html', {})


def landscape(request):
    return render(request, 'web_app/landscape_design.html', {})


def outdoor(request):
    return render(request, 'web_app/outdoor_remodel.html', {})


def indoor(request):
    return render(request, 'web_app/indoor_remodel.html', {})


def gallery(request):
    photo = GalleryUpload.objects.all()
    return render(request, 'web_app/gallery.html', {'photos': photo})


def contact(request):
    if request.method=="POST":
        first_name = request.POST['name']
        email = request.POST['email']
        subject = request.POST['subject']
        message = request.POST['message']
        ins = ClientLeads(first_name=first_name,email=email,subject=subject,message=message)
        ins.save()

        msg_mail = "Name: " + str(first_name) + "\n\nEmail: " + str(email) + "\n\nSubject: " + str(subject) + "\n\nMessage: " + str(message)
        # Send Email
        send_mail(
            'Torres Contact Form by: ' + first_name,  # subject
            msg_mail,
            email,
            ['torresyardworks@gmail.com'],  # to email
            fail_silently=False,
        )
        print("Data has been written in db.")
        return render(request, 'web_app/thank_you.html', {'first_name': first_name})
    else:
        return render(request, 'web_app/contact.html', {})
    

def free_quote(request):
    if request.method=="POST":
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        phone = request.POST['phone']
        address = request.POST['address']
        date = request.POST['date']
        service = request.POST['service']
        message = request.POST['message']
        ins = ClientLeads(first_name=first_name,last_name=last_name,email=email,phone=phone,address=address,date=date,service=service,message=message)
        ins.save()

        msg_mail = "Name: " + str(first_name) + " " + str(last_name) + "\n\nEmail: " + str(email) + "\n\nPhone: " + str(phone) + "\n\nAddress: " + str(address) + "\n\nDate: " + str(date) + "\n\nService: " + str(service) + "\n\nMessage: " + str(message)
        # Send Email
        send_mail(
            'Torres Request Form by: ' + first_name + " " + last_name,  # subject
            msg_mail,
            email,
            ['torresyardworks@gmail.com'],  # to email
            fail_silently=False,
        )
        print("Data has been written in db.")
        return render(request, 'web_app/thank_you.html', {'first_name': first_name})
    else:
        return render(request, 'web_app/request_quote.html', {})


def thank_you(request):
    return render(request, 'web_app/thank_you.html', {})

# Test page for models and forms
def test(request):
    return render(request, 'web_app/test.html')
