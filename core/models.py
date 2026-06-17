from django.db import models

class NewsletterSubscriber(models.Model):
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.email

class PlatformTestimonial(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='platform_testimonials')
    content = models.TextField()
    rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Testimonial from {self.user.username} ({self.rating} stars)"