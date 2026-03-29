from django import forms
from .models import Project, Category


class ProjectUploadForm(forms.ModelForm):

    class Meta:
        model = Project
        fields = [
            'title', 'category', 'description', 'technology',
            'difficulty_level', 'version', 'requirements',
            'price', 'thumbnail', 'demo_video_url',
            'installation_video_url', 'zip_file',
            'documentation_file', 'file_size'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Project Title'
            }),
            'category': forms.Select(attrs={
                'class': 'form-select'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 4,
                'placeholder': 'Project Description'
            }),
            'technology': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'e.g. Django, Python'
            }),
            'difficulty_level': forms.Select(attrs={
                'class': 'form-select'
            }),
            'version': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'e.g. 1.0.0'
            }),
            'requirements': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 3,
                'placeholder': 'e.g. Python 3.10, Django 4.2'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control', 'placeholder': 'Price in ₹'
            }),
            'thumbnail': forms.FileInput(attrs={
                'class': 'form-control'
            }),
            'demo_video_url': forms.URLInput(attrs={
                'class': 'form-control', 'placeholder': 'YouTube Demo URL'
            }),
            'installation_video_url': forms.URLInput(attrs={
                'class': 'form-control', 'placeholder': 'YouTube Installation URL'
            }),
            'zip_file': forms.FileInput(attrs={
                'class': 'form-control'
            }),
            'documentation_file': forms.FileInput(attrs={
                'class': 'form-control'
            }),
            'file_size': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'e.g. 2.5 MB'
            }),
        }