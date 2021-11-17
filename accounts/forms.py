from django import forms
from .models import Payee, Transaction


class UploadFileForm(forms.ModelForm):
    statement = forms.FileField()

    class Meta:
        model = Transaction
        fields = ['account']
    

class PayeeForm(forms.ModelForm):
    class Meta:
        model = Payee
        fields = ['name', 'alias']


class DateInput(forms.DateInput):
    input_type = 'date'


class DateForm(forms.Form):
    date = forms.DateField(widget=DateInput)

    