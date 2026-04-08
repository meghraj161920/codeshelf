from django.db import models
from django.utils.text import slugify


class CourseCategory(models.Model):
    """
    Stores course categories.
    Examples: Python, Django, Web Development, Machine Learning
    slug is used in URL filters e.g. /courses/?category=python
    """
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Course Categories'

    def __str__(self):
        return self.name


class Course(models.Model):
    """
    Main course model.
    Each course belongs to one category.
    Each course has multiple videos (CourseVideo).
    slug is auto-generated from title on save.
    total_videos is a property that counts related videos.
    """
    DIFFICULTY_CHOICES = (
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    )

    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()

    category = models.ForeignKey(
        CourseCategory,
        on_delete=models.CASCADE,
        related_name='courses'
    )

    thumbnail = models.ImageField(upload_to='course_thumbnails/')
    difficulty_level = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def total_videos(self):
        """Returns total number of videos in this course."""
        return self.videos.count()

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class CourseVideo(models.Model):
    """
    Individual video inside a course.
    youtube_url must be in embed format:
    https://www.youtube.com/embed/VIDEO_ID
    order field decides the sequence of videos.
    duration is optional e.g. 10:30
    """
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='videos'
    )

    title = models.CharField(max_length=255)
    youtube_url = models.URLField(help_text="Use embed URL: https://www.youtube.com/embed/VIDEO_ID")
    order = models.PositiveIntegerField(default=1)
    duration = models.CharField(max_length=20, blank=True, help_text="e.g. 10:30")

    # NEW FIELD - paste HTML notes content here
    notes = models.TextField(
        blank=True,
        null=True,
        help_text="Paste full HTML notes content for this video topic."
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.course.title} - {self.order}. {self.title}"

