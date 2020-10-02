from django import forms


class SearchQuery(forms.Form):
    query = forms.CharField(widget=forms.TextInput)