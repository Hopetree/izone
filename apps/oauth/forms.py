# -*- coding: utf-8 -*-
from django import forms
from .models import Ouser

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Ouser
        fields = ['link','avatar']






