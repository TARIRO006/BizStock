from django.contrib import admin
from .models import Category, Product

# Register your models here.

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):

    list_display = (
        'name',
        'business',
        'created_at',
    )

    list_filter = (
        'business',
    )

    search_fields = (
        'name',
    )


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):

    list_display = (
        'name',
        'sku',
        'category',
        'business',
        'unit',
        'cost_price',
        'selling_price',
        'minimum_stock',
        'is_active',
    )

    list_filter = (
        'business',
        'category',
        'unit',
        'is_active',
    )

    search_fields = (
        'name',
        'sku',
    )