from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from embed_video.fields import EmbedVideoField


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Project(models.Model):
    DIFFICULTY_CHOICES = (
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    )

    seller = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='projects'
    )

    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True, db_index=True)

    description = models.TextField()

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='projects'
    )

    technology = models.CharField(max_length=100, db_index=True)

    difficulty_level = models.CharField(
        max_length=20,
        choices=DIFFICULTY_CHOICES,
        db_index=True
    )

    version = models.CharField(max_length=50)
    requirements = models.TextField()

    price = models.DecimalField(max_digits=10, decimal_places=2)

    thumbnail = models.ImageField(upload_to='project_images/')

    demo_video_url = EmbedVideoField(blank=True, null=True)
    installation_video_url = EmbedVideoField(blank=True, null=True)

    zip_file = models.FileField(upload_to='project_files/')
    documentation_file = models.FileField(upload_to='project_docs/', blank=True, null=True)

    file_size = models.CharField(max_length=50, blank=True)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    @property
    def average_rating(self):
        reviews = self.reviews.all()
        if reviews:
            return round(sum(r.rating for r in reviews) / len(reviews), 1)
        return 0

    @property
    def review_count(self):
        return self.reviews.count()

    @property
    def render_stars(self):
        from django.utils.safestring import mark_safe
        avg = self.average_rating
        full_stars = int(avg)
        half_star = 1 if avg - full_stars >= 0.5 else 0
        empty_stars = 5 - full_stars - half_star
        
        html = '<i class="fa-solid fa-star"></i>' * full_stars
        if half_star:
            html += '<i class="fa-solid fa-star-half-stroke"></i>'
        html += '<i class="fa-regular fa-star"></i>' * empty_stars
        
        return mark_safe(html)

    @property
    def total_downloads(self):
        # Support for view annotations to avoid N+1 queries
        if hasattr(self, '_total_downloads_annotated'):
            return self._total_downloads_annotated
        from django.db.models import Sum
        total = self.downloads.aggregate(total=Sum('download_count'))['total']
        return total if total else 0

    @total_downloads.setter
    def total_downloads(self, value):
        self._total_downloads_annotated = value

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} ({self.seller.username})"


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