from django import forms


class PlaceholderForm(forms.Form):
    query = forms.CharField(max_length=100, required=False)
