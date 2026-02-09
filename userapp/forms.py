from django import forms


class CheckoutForm(forms.Form):
    customer_name = forms.CharField(label='Full name', max_length=150)
    email = forms.EmailField()
    phone = forms.CharField(label='Phone number', max_length=20)
    address = forms.CharField(widget=forms.Textarea(attrs={'rows': 2}))
    city = forms.CharField(max_length=100)
    state = forms.CharField(max_length=100)
    postal_code = forms.CharField(label='Postal code', max_length=20)
    notes = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False)
