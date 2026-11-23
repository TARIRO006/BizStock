from django.db import models

# Create your models here.

class Business(models.Model):
    BUSINESS_TYPES = [
        ('retail', 'Retail'),
        ('manufacturing', 'Manufacturing'),
        ('both', 'Retail & Manufacturing'),
    ]

    CURRENCY_CHOICES = [
    ('MWK', 'Malawian Kwacha (MWK)'),
    ('USD', 'US Dollar (USD)'),
    ('GBP', 'British Pound (GBP)'),
    ('ZAR', 'South African Rand (ZAR)'),
    ('EUR', 'Euro (EUR)'),
    ('KES', 'Kenyan Shilling (KES)'),
    ('TZS', 'Tanzanian Shilling (TZS)'),
    ('ZMW', 'Zambian Kwacha (ZMW)'),
    ]

    name = models.CharField(max_length=200)
    business_type = models.CharField(
        max_length=20,
        choices=BUSINESS_TYPES
    )
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    address = models.TextField(blank=True)
    logo = models.ImageField(upload_to='business_logos/', blank=True, null=True)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='MWK')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name