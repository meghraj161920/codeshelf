from django.db import models
from django.contrib.auth.models import User
from projects.models import Project
from courses.models import Course


class Wishlist(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='wishlist'
    )

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='wishlisted_by',
        null=True, 
        blank=True
    )

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='wishlisted_by',
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'project'], name='unique_user_project'),
            models.UniqueConstraint(fields=['user', 'course'], name='unique_user_course'),
        ]

    def __str__(self):
        item_name = self.project.title if self.project else (self.course.title if self.course else "Unknown")
        return f"{self.user.username} - {item_name}"