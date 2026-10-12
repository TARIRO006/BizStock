from django.contrib import admin
from .models import Category, Product, Supplier, Purchase, PurchaseItem

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


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):

    list_display = (
        'name',
        'contact_person',
        'phone',
        'email',
        'is_active',
    )

    list_filter = ('is_active',)

    search_fields = (
        'name',
        'contact_person',
        'phone',
        'email',
    )


class PurchaseItemInline(admin.TabularInline):
    model = PurchaseItem
    extra = 1


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):

    list_display = (
        'reference',
        'supplier',
        'location',
        'status',
        'created_at',
        'received_at',
    )

    list_filter = (
        'status',
        'created_at',
    )

    search_fields = (
        'reference',
        'supplier__name',
    )

    inlines = [PurchaseItemInline]


@admin.register(PurchaseItem)
class PurchaseItemAdmin(admin.ModelAdmin):

    list_display = (
        'purchase',
        'product',
        'quantity',
        'unit_cost',
    )
