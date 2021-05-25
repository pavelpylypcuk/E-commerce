from django import forms

class CreateForm(forms.Form):
    name = forms.CharField(label='Name', max_length=50)
    price = forms.DecimalField(label="Price", min_value="0.1", required=False)
    description = forms.CharField(label="Description", max_length=50)
    url = forms.URLField(label="URL", required=False)
    category = forms.CharField(label="Category", max_length=50)