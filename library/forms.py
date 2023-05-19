from django import forms
from .models import AuthUser, Books, Comments

class ProfileForm(forms.ModelForm):
    class Meta:
        model = AuthUser
        fields = ['first_name', 'last_name', 'email']

class AddBookForm(forms.Form):
    isbn = forms.CharField(max_length=50)
    title = forms.CharField(max_length=50)
    authors = forms.CharField(max_length=50)
    publisher = forms.CharField(max_length=50)
    price = forms.FloatField()
    lno = forms.ChoiceField(choices=(
        ('1', 'Ziuzino Library'),
        ('2', 'Dolgoprudny Library I'),
        ('3', 'Zhukovski Library'),
        ('4', 'Dolgoprudny Library II')
    ))
    lno.widget.attrs.update({'class': 'dropdown-trigger waves-effect'})

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comments
        fields = ['text']

class ReserveForm(forms.Form):
    lno = forms.ChoiceField(choices=(
        ('1', 'Ziuzino Library'),
        ('2', 'Dolgoprudny Library I'),
        ('3', 'Zhukovski Library'),
        ('4', 'Dolgoprudny Library II')
    ))
    lno.widget.attrs.update({'class': 'dropdown-trigger waves-effect'})

class SearchBookForm(forms.Form):
    text = forms.CharField(max_length=50, required=False)
