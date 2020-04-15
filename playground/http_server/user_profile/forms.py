from django import forms

class NewPostForm(forms.Form):
    text = forms.CharField(label='text', max_length=256)

class SearchUserForm(forms.Form):
    username = forms.CharField(label='username', max_length=256)
