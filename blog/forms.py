from django import forms

from .models import Comment


class EmailForm(forms.Form):
    email_from = forms.EmailField()
    email_to = forms.EmailField()
    subject = forms.CharField()
    comment = forms.CharField(required=False, widget=forms.Textarea)


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('name', 'email', 'body',)


class SearchForm(forms.Form):
    query = forms.CharField()
