from django.db import models
from django.utils.text import slugify
from embed_video.fields import EmbedVideoField


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

    seller = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE,
        related_name='courses',
        null=True,  # Initially allow null to handle migrations
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
    
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_free = models.BooleanField(default=False)

    ACCESS_DURATION_CHOICES = (
        (0, 'Lifetime'),
        (3, '3 Months'),
        (6, '6 Months'),
    )
    access_duration_months = models.IntegerField(choices=ACCESS_DURATION_CHOICES, default=0, help_text="0 means lifetime access")

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def total_videos(self):
        """Returns total number of videos in this course."""
        return self.videos.count()

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
    youtube_url = EmbedVideoField(help_text="Paste normal YouTube URL")
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

