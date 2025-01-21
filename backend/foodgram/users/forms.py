from django import forms
from .models import User

class SubscribeForm(forms.ModelForm):
    class Meta:
        model = User
        fields = []