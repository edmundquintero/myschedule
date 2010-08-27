from django import forms

class search_form(forms.Form):
    search_text = forms.CharField()
