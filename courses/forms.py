from django import forms
from .models import Course

class CourseUploadForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = [
            'title', 'category', 'description', 'thumbnail', 
            'difficulty_level', 'price', 'is_free', 
            'access_duration_months', 'is_active'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Full Stack Web Development'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Describe what students will learn...'}),
            'thumbnail': forms.FileInput(attrs={'class': 'form-control'}),
            'difficulty_level': forms.Select(attrs={'class': 'form-select'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00'}),
            'is_free': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'access_duration_months': forms.Select(attrs={'class': 'form-select'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
