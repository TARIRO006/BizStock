from django.contrib import admin
from .models import Business


# Register your models here.

@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'business_type',
        'email',
        'phone',
        'created_at',
    )

    search_fields = (
        'name',
        'email',
    )

    list_filter = (
        'business_type',
        'created_at',
    )