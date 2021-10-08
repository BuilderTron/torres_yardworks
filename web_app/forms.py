from django import forms
from .models import ClientLeads

class ReqForm(forms.ModelForm):
    class Meta:
        model = ClientLeads
        fields = ("first_name", "last_name", "email", "phone", "address", "date", "service", "message")