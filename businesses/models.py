from django.db import models

# Create your models here.

class Business(models.Model):
    BUSINESS_TYPES = [
        ('retail', 'Retail'),
        ('manufacturing', 'Manufacturing'),
        ('both', 'Retail & Manufacturing'),
    ]

    name = models.CharField(max_length=200)
    business_type = models.CharField(
        max_length=20,
        choices=BUSINESS_TYPES
    )
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    address = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name