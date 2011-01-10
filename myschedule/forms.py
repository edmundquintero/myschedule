from django import forms

class search_form(forms.Form):
    query =  forms.CharField()
