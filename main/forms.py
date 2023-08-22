from django import forms

acces_choices = (('Closed','Closed'),
               ('Limited','Limited'),
               ('Public','Public'))
class Storage_form(forms.Form):
    acces = forms.ChoiceField(choices=acces_choices,label='Доступ')

class Settings_form(forms.Form):
    acces = forms.ChoiceField(choices=acces_choices,label='Доступ к вашему хранилищу')

