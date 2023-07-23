from django.contrib.auth.models import User
from django import forms
from .models import Profile, Video


class UpdateVideoForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = ['title', 'description', 'tags']


class UploadVideoForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = ['title', 'description', 'video', 'thumbnail', 'tags']


class ResetPasswordForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['password']


class EditAvatarForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['image']


class UserRegFrom(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']