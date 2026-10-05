from django.contrib import admin
from .models import Location, Stock, StockMovement

# Register your models here.

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):

    list_display = (
        'name',
        'business',
        'location_type',
        'phone',
        'is_active',
        'created_at',
    )

    list_filter = (
        'business',
        'location_type',
        'is_active',
    )

    search_fields = (
        'name',
        'address',
        'phone',
    )


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):

    list_display = (
        'product',
        'location',
        'business',
        'quantity',
        'updated_at',
    )

    list_filter = (
        'business',
        'location',
    )

    search_fields = (
        'product__name',
        'location__name',
    )


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):

    list_display = (
        'product',
        'location',
        'movement_type',
        'quantity',
        'reference',
        'created_by',
        'created_at',
    )

    list_filter = (
        'business',
        'movement_type',
        'location',
        'created_at',
    )

    search_fields = (
        'product__name',
        'location__name',
        'reference',
        'notes',
    )