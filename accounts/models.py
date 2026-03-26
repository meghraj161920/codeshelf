from django.contrib.auth.models import User
from django.db import models


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")

    ROLE_CHOICES = [
        ('customer', 'Customer'),
        ('seller', 'Seller')
    ]

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='customer')

    dob = models.DateField(null=True, blank=True)

    gender = models.CharField(
        max_length=10,
        choices=[
            ('male', 'Male'),
            ('female', 'Female')
        ],
        null=True,
        blank=True
    )

    phone_number = models.CharField(max_length=15, blank=True)

    profile_image = models.ImageField(
        upload_to='profiles/',
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    # 🔥 HELPER METHODS (VERY USEFUL)
    @property
    def is_seller(self):
        return self.role == 'seller'

    @property
    def is_customer(self):
        return self.role == 'customer'

    def __str__(self):
        return f"{self.user.username} ({self.role})"