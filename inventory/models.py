from django.db import models
from businesses.models import Business
from django.conf import settings
from django.core.validators import MinValueValidator
from django.utils import timezone
from decimal import Decimal

# Create your models here.

class Category(models.Model):
    business = models.ForeignKey(
        Business,
        on_delete=models.CASCADE,
        related_name='categories'
    )

    name = models.CharField(max_length=100)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name


class Product(models.Model):

    UNIT_CHOICES = [
        ('piece', 'Piece'),
        ('kg', 'Kilogram'),
        ('g', 'Gram'),
        ('litre', 'Litre'),
        ('ml', 'Millilitre'),
        ('box', 'Box'),
        ('pack', 'Pack'),
        ('dozen', 'Dozen'),
    ]

    business = models.ForeignKey(
        Business,
        on_delete=models.CASCADE,
        related_name='products'
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products'
    )

    name = models.CharField(max_length=200)

    sku = models.CharField(
        max_length=100,
        blank=True
    )

    description = models.TextField(
        blank=True
    )

    unit = models.CharField(
        max_length=20,
        choices=UNIT_CHOICES,
        default='piece'
    )

    cost_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    selling_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    minimum_stock = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name



class Supplier(models.Model):

    business = models.ForeignKey(
        Business,
        on_delete=models.CASCADE,
        related_name='suppliers'
    )

    name = models.CharField(max_length=200)

    contact_person = models.CharField(
        max_length=150,
        blank=True
    )

    email = models.EmailField(blank=True)

    phone = models.CharField(
        max_length=30,
        blank=True
    )

    address = models.TextField(blank=True)

    notes = models.TextField(blank=True)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name




class Purchase(models.Model):

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('received', 'Received'),
        ('cancelled', 'Cancelled'),
    ]

    business = models.ForeignKey(
        Business,
        on_delete=models.CASCADE,
        related_name='purchases'
    )

    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.PROTECT,
        related_name='purchases'
    )

    location = models.ForeignKey(
        'shops.Location',
        on_delete=models.PROTECT,
        related_name='purchases'
    )

    reference = models.CharField(
        max_length=100,
        blank=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft'
    )

    notes = models.TextField(blank=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    received_at = models.DateTimeField(
        null=True,
        blank=True
    )

    class Meta:
        ordering = ['-created_at']

    @property
    def total_cost(self):
        return sum(
            (item.line_total for item in self.items.all()),
            start=Decimal('0.00')
        )

    def __str__(self):
        return self.reference or f'Purchase #{self.pk}'


class PurchaseItem(models.Model):

    purchase = models.ForeignKey(
        Purchase,
        on_delete=models.CASCADE,
        related_name='items'
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name='purchase_items'
    )

    quantity = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )

    unit_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )

    @property
    def line_total(self):
        return self.quantity * self.unit_cost

    def __str__(self):
        return f'{self.product.name} - {self.quantity}'

