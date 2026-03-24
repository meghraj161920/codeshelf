from django.db import models
from django.contrib.auth.models import User
from projects.models import Project


class Wishlist(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='wishlist'
    )

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='wishlisted_by'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'project') 

    def __str__(self):
        return f"{self.user.username} - {self.project.title}"