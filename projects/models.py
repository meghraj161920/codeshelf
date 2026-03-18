from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Project(models.Model):
    DIFFICULTY_CHOICES = (
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    )

    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField()

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='projects'
    )

    technology = models.CharField(max_length=100)
    difficulty_level = models.CharField(
        max_length=20,
        choices=DIFFICULTY_CHOICES
    )

    version = models.CharField(max_length=50)
    requirements = models.TextField()

    price = models.DecimalField(max_digits=10, decimal_places=2)

    thumbnail = models.ImageField(upload_to='project_images/')

    demo_video_url = models.URLField()
    installation_video_url = models.URLField()

    zip_file = models.FileField(upload_to='project_files/')
    documentation_file = models.FileField(upload_to='project_docs/')

    file_size = models.CharField(max_length=50)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class ProjectImage(models.Model):
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='images'
    )

    image = models.ImageField(upload_to='project_images/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.project.title} Image"


class ProjectDownload(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='downloads'
    )

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='downloads'
    )

    download_count = models.PositiveIntegerField(default=0)

    last_downloaded = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.project.title}"