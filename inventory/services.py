
from django.db import transaction
from django.utils import timezone

from .models import Purchase
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
