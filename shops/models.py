from django.db import models
from businesses.models import Business

# Create your models here.

class Location(models.Model):

    LOCATION_TYPES = [
        ('factory', 'Factory'),
        ('shop', 'Shop'),
    ]

    business = models.ForeignKey(
        Business,
        on_delete=models.CASCADE,
        related_name='locations'
    )

    name = models.CharField(
        max_length=150
    )

    location_type = models.CharField(
        max_length=20,
        choices=LOCATION_TYPES
    )

    address = models.TextField(
        blank=True
    )

    phone = models.CharField(
        max_length=30,
        blank=True
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Stock(models.Model):

    business = models.ForeignKey(
        Business,
        on_delete=models.CASCADE,
        related_name='stock_records'
    )

    location = models.ForeignKey(
        Location,
        on_delete=models.CASCADE,
        related_name='stock_records'
    )

    product = models.ForeignKey(
        'inventory.Product',
        on_delete=models.CASCADE,
        related_name='stock_records'
    )

    quantity = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    'location',
                    'product'
                ],
                name='unique_product_location_stock'
            )
        ]

        ordering = ['product__name']

    def __str__(self):
        return f'{self.product.name} - {self.location.name}'