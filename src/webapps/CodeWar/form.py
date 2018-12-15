from django import forms

from .models import *


class UserForm(forms.Form):
    username = forms.CharField(max_length=20,
                               widget=forms.TextInput(attrs={'placeholder': 'Username', 'class': 'form-control'}))
    password = forms.CharField(max_length=200, label='Password',
                               widget=forms.PasswordInput(attrs={'placeholder': 'Password', 'class': 'form-control'}))

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        if not (username or password):
            raise forms.ValidationError("Information is in complete")
        return self.cleaned_data

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'


class RegistForm(forms.Form):
    username = forms.CharField(max_length=200)
    first_name = forms.CharField(max_length=200)
    last_name = forms.CharField(max_length=200)
    age = forms.IntegerField()
    bio = forms.CharField(max_length=420)
    email = forms.EmailField()
    password1 = forms.CharField(max_length=200, label="Password", widget=forms.PasswordInput())
    password2 = forms.CharField(max_length=200, label="Confirm Password", widget=forms.PasswordInput())

    def clean(self):
        cleaned_data = super(RegistForm, self).clean()
        username = cleaned_data.get('username')
        first_name = cleaned_data.get('first_name')
        last_name = cleaned_data.get('last_name')
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        age = cleaned_data.get('age')
        bio = cleaned_data.get('bio')
        email = cleaned_data.get('email')
        if not (username or first_name or last_name or password1 or password2 or age or bio or email):
            raise forms.ValidationError("Information is not complete")
        if password1 != password2:
            raise forms.ValidationError("Passwords are not same")

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username):
            raise forms.ValidationError("Username is occupied")
        return username

    def clean_age(self):
        age = self.cleaned_data.get('age')
        if age < 0:
            raise forms.ValidationError("age could not be negative")
        return age


class UserMetaForm(forms.ModelForm):
    password1 = forms.CharField(max_length=200, label="Password", widget=forms.PasswordInput(), required=False)
    password2 = forms.CharField(max_length=200, label="Confirm Password", widget=forms.PasswordInput(), required=False)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')

    def clean(self):
        cleaned_data = super(UserMetaForm, self).clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        if not password1 or not password2:
            cleaned_data.pop('password1')
            cleaned_data.pop('password2')
            return cleaned_data
        elif password1 != password2:
            raise forms.ValidationError(
                "password and confirm_password does not match"
            )

        return cleaned_data


class CodingUserForm(forms.ModelForm):
    class Meta:
        model = CodingUser
        fields = ('age', 'bio', 'picture')
        widgets = {'picture': forms.FileInput()}
