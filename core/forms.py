from django import forms
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget

PAYMENT_CHOICES = (
    ('S', 'Credit/Debit Card'),
    ('P', 'PayPal')
)


class CheckoutForm(forms.Form):
    street_address = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': 'Address',
        'class': 'form-control'
    }))
    apartment_address = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'placeholder': 'Address line 2 (Optional)',
        'class': 'form-control'
    }))
    country = CountryField(blank_label='(select country)').formfield(
        widget=CountrySelectWidget(
            attrs={"class": "custom-select d-block w-100"}
        )
    )

    zipc = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': 'Zip Code',
        'class': 'form-control'
    }))
    payment_option = forms.ChoiceField(
        widget=forms.RadioSelect(), choices=PAYMENT_CHOICES)
