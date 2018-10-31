from django import forms

class NameForm(forms.Form):
    your_name = forms.CharField(label='Your name', max_length=100)

class Search_Form(forms.Form):
    search_query = forms.CharField(label='Search', max_length=100)
