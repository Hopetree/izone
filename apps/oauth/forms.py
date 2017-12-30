# -*- coding: utf-8 -*-
from django import forms
from .models import Ouser

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Ouser
        fields = ['nickname','link','avatar']

    def clean_nickname(self):
        nickname =  self.cleaned_data.get('nickname')
        if len(nickname) < 2:
            raise forms.ValidationError('昵称必须多于2个字符！')
        return nickname





