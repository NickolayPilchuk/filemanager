from django import forms
from .models import Comments

class Comment_form(forms.ModelForm):
    class Meta:
        model = Comments
        fields = ('text',)