from django import forms

from alphatracker.models import Company
from alphatracker.widget import DatePickerInput


class addCompanyForm(forms.Form):
    name = forms.CharField(required="True",
                           max_length=50,
                           widget=forms.TextInput(attrs={'id': 'id_company_name'}),
                           )
    account = forms.CharField(required="True",
                              max_length=50,
                              widget=forms.TextInput(attrs={'id': 'id_company_account'}),
                              )
    url = forms.CharField(required="True",
                          max_length=50,
                          widget=forms.TextInput(attrs={'id': 'id_company_url'}),)
    establish_time = forms.DateField(widget=DatePickerInput)
    size = forms.IntegerField(required="True",
                              widget=forms.NumberInput(attrs={'id': 'id_company_size'}),
                              )

# class Meta:
    #     model = Company
    #     fields = ('name', 'account', 'url', 'establish_time', 'size')
    #     widgets = {
    #         'name': forms.TextInput(attrs={'id': 'id_company_name'}),
    #         'account': forms.TextInput(attrs={'id': 'id_company_account'}),
    #         'url': forms.URLInput(attrs={'id': 'id_company_url'}),
    #         'establish_time': forms.DateInput(attrs={'id': 'id_company_establish_time'}),
    #         'size': forms.NumberInput(attrs={'id': 'id_company_size'})
    #     }
    #     labels = {
    #         'name': 'Company Name',
    #         'account': "Company Twitter Account",
    #         'url': "Company URL",
    #         'establish_time': "Company Establish Time",
    #         'size': "Company Size",
    #     }

