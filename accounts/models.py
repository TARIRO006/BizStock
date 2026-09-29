from django.db import models
from django.contrib.auth.models import User
from businesses.models import Business

# Create your models here.

class UserProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )

    business = models.ForeignKey(
        Business,
        on_delete=models.CASCADE,
        related_name='users'
    )

    def __str__(self):
        return f"{self.user.username} - {self.business.name}"