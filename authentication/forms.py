# forms.py
from django import forms
from .models import *
from authentication.models import Profile
  
class ProfileForm(forms.ModelForm):
  
    class Meta:
        model = Profile
        fields = ['profile_pic']