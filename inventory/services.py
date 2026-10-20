
from django.db import transaction
from django.utils import timezone

from .models import Purchase, Sale
from shops.services import create_stock_movement


@transaction.atomic
def receive_purchase(*, purchase_id, business, user=None):
    # Lock the purchase row while receiving it.
    purchase = (
        Purchase.objects
        .select_for_update()
        .select_related('supplier', 'location')
        .get(id=purchase_id, business=business)
    )

    # A purchase must only be received once.
    if purchase.status != 'draft':
        raise ValueError(
            'Only draft purchases can be received.'
        )

    items = list(
        purchase.items.select_related('product').all()
    )

    if not items:
        raise ValueError(
            'Cannot receive a purchase without products.'
        )

    # Verify that the related records belong to this business.
    if purchase.supplier.business_id != business.id:
        raise ValueError('The supplier belongs to another business.')

    if purchase.location.business_id != business.id:
        raise ValueError('The location belongs to another business.')

    for item in items:
        if item.product.business_id != business.id:
            raise ValueError(
                'A product belongs to another business.'
            )

    # Add stock and create a movement for every purchase item.
    for item in items:
        create_stock_movement(
            business=business,
            product=item.product,
            location=purchase.location,
            movement_type='purchase',
            quantity=item.quantity,
            user=user,
            reference=purchase.reference or f'PUR-{purchase.pk}',
            notes=f'Received from supplier: {purchase.supplier.name}',
        )

    # Mark as received only after all stock updates succeed.
    purchase.status = 'received'
    purchase.received_at = timezone.now()
    purchase.save(update_fields=['status', 'received_at'])

    return purchase



@transaction.atomic
def complete_sale(*, sale_id, business, user=None):
    # Lock the sale so two requests cannot complete it simultaneously.
    sale = Sale.objects.select_for_update().get(
        pk=sale_id,
        business=business,
    )

    if sale.status != 'draft':
        raise ValueError(
            'Only draft sales can be completed.'
        )

    items = list(
        sale.items.select_related('product').all()
    )

    if not items:
        raise ValueError(
            'Cannot complete a sale without products.'
        )

    # Validate all products before processing stock movements.
    for item in items:
        if item.product.business_id != business.pk:
            raise ValueError(
                'A sale contains a product from another business.'
            )

    if sale.location.business_id != business.pk:
        raise ValueError(
            'The selected shop does not belong to this business.'
        )

    # Each movement deducts stock and creates a stock history record.
    # If any movement fails, the entire transaction rolls back.
    for item in items:
        create_stock_movement(
            business=business,
            product=item.product,
            location=sale.location,
            movement_type='sale',
            quantity=item.quantity,
            user=user,
            reference=sale.reference or f'SALE-{sale.pk}',
            notes=f'Sale #{sale.pk} completed.',
        )

    sale.status = 'completed'
    sale.completed_at = timezone.now()
    sale.save(update_fields=['status', 'completed_at'])

    return sale

