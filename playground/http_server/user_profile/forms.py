from django import forms

class NewPostForm(forms.Form):
    text = forms.CharField(label='text', max_length=256)
