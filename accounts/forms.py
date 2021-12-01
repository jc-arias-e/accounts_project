from django import forms
from .models import Alias, DoubleEntry, Payee, Transaction


class UploadFileForm(forms.ModelForm):
    statement = forms.FileField()

    class Meta:
        model = Transaction
        fields = ['account']
    

class PayeeForm(forms.ModelForm):
    class Meta:
        model = Payee
        fields = ['name', 'alias']


class AliasForm(forms.ModelForm):
    double_entry = forms.BooleanField(required=False)

    class Meta:
        model = Alias
        fields = ['name', 'category', 'subcategory']
        

class DoubleEntryForm(forms.ModelForm):
    class Meta:
        model = DoubleEntry
        fields = ['alias', 'account_a', 'account_b']
        

class DateInput(forms.DateInput):
    input_type = 'date'


class DateForm(forms.Form):
    date = forms.DateField(widget=DateInput)

    