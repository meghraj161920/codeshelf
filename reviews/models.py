from django.db import models
from django.contrib.auth.models import User
from projects.models import Project
from courses.models import Course

class Review(models.Model):
    RATING_CHOICES = (
        (1, '1 Star'),
        (2, '2 Stars'),
        (3, '3 Stars'),
        (4, '4 Stars'),
        (5, '5 Stars'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='reviews', null=True, blank=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='reviews', null=True, blank=True)

    rating = models.IntegerField(choices=RATING_CHOICES)
    review_text = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'project'], condition=models.Q(project__isnull=False), name='unique_user_project_review'),
            models.UniqueConstraint(fields=['user', 'course'], condition=models.Q(course__isnull=False), name='unique_user_course_review'),
        ]

    def __str__(self):
        item_title = self.project.title if self.project else (self.course.title if self.course else 'Unknown')
        return f"{self.user.username} - {item_title} ({self.rating})"