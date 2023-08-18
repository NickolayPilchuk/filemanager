from django import forms
from .models import Comments
from django.contrib.auth.forms import UserCreationForm
acces_choices = (('Closed','Closed'),
               ('Limited','Limited'),
               ('Public','Public'))
class Storage_form(forms.Form):
    acces = forms.ChoiceField(choices=acces_choices,label='Доступ')

class Settings_form(forms.Form):
    acces = forms.ChoiceField(choices=acces_choices,label='Доступ к вашему хранилищу')

class Comment_form(forms.ModelForm):
    class Meta:
        model = Comments
        fields = ('text',)