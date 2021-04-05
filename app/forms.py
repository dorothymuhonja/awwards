from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile, Project, Rating, Comment

class SignupForm(UserCreationForm):
    email = forms.EmailField(max_length=250, help_text='Required. Please enter a valid email address')

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['project_name', 'image', 'description']


class EditProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        exclude = ['user']


class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ['design', 'usability', 'content']


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        exclude = ['project','profile']
