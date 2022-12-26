from dataclasses import fields
from pyexpat import model
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm, SetPasswordForm
from django.contrib.auth.models import User
from django import forms
from django.forms import ModelForm
from page3.models import Profile
# from PostIT.page3.models import Profile


class SignUpForm(UserCreationForm):
    email = forms.EmailField(widget=forms.EmailInput(
        attrs={'class': 'form-control', 'placeholder': 'Email'}), required=False)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['class'] = 'form-control'
        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].widget.attrs['class'] = 'form-control'


class EditProfileForm(UserChangeForm):
    password = None
    email = forms.EmailField(widget=forms.EmailInput(
        attrs={'class': 'form-control', 'placeholder': 'Email'}), required=False)
    username = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'username'}))
    # password = forms.CharField(widget=forms.PasswordInput(
    #     attrs={'class': 'form-control', 'placeholder': 'password', 'type': 'password'}))

    class Meta:
        model = User
        fields = ('username', 'email')


class PasswordChangingForm(SetPasswordForm):
    new_password1 = forms.CharField(widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'placeholder': 'password', 'type': 'password'}))
    new_password2 = forms.CharField(widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'placeholder': 'confirm password', 'type': 'password'}))

    class Meta:
        model = User
        fields = ('new_password1', 'new_password2')


choices = [('VALORANT', 'VALORANT'), ('CSGO', 'CSGO'), ('COD', 'COD')]


class ProfileForm(ModelForm):
    class Meta:
        model = Profile
        # fields = '__all__'
        fields = ('bio', 'profile_pic', 'discord_link', 'twitch_link')
        widgets = {
            'bio': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Add a bio...'}),
            'discord_link': forms.TextInput(attrs={'class': 'form-control', 'placeholder': ''}),
            'twitch_link': forms.TextInput(attrs={'class': 'form-control', 'placeholder': ''}),
        }
