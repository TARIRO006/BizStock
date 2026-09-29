from django.contrib import admin
from .models import Location, Stock

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