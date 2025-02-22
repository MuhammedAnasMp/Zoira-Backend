from django import forms
from apps.purchase.models import Customer, HennaSale,HennaType

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'contact_info']

class HennaSaleForm(forms.ModelForm):
    class Meta:
        model = HennaSale
        fields = ['henna_type', 'customer', 'quantity_sold', 'sale_price_per_unit']


class HennaTypeForm(forms.ModelForm):
    class Meta:
        model = HennaType
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded', 'placeholder': 'Henna Type Name'}),
        }