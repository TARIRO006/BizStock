from django.db import transaction
from django.db.models import F

from .models import Stock, StockMovement


@transaction.atomic
def create_stock_movement(
    *,
    business,
    product,
    location,
    movement_type,
    quantity,
    user=None,
    reference='',
    notes=''
):

    if quantity <= 0:
        raise ValueError(
            'Movement quantity must be greater than zero.'
        )

    stock, created = Stock.objects.select_for_update().get_or_create(
        business=business,
        location=location,
        product=product,
        defaults={
            'quantity': 0
        }
    )

    incoming_types = [
        'purchase',
        'transfer_in',
        'production',
        'adjustment',
    ]

    outgoing_types = [
        'sale',
        'transfer_out',
        'consumption',
    ]

    if movement_type in incoming_types:

        stock.quantity = F('quantity') + quantity

    elif movement_type in outgoing_types:

        if stock.quantity < quantity:
            raise ValueError(
                'Insufficient stock available.'
            )

        stock.quantity = F('quantity') - quantity

    else:

        raise ValueError(
            'Invalid stock movement type.'
        )

    stock.save(
        update_fields=[
            'quantity',
            'updated_at',
        ]
    )

    stock.refresh_from_db()

    movement = StockMovement.objects.create(
        business=business,
        product=product,
        location=location,
        movement_type=movement_type,
        quantity=quantity,
        reference=reference,
        notes=notes,
        created_by=user,
    )

    return movement


@transaction.atomic
def transfer_stock(
    *,
    business,
    product,
    source_location,
    destination_location,
    quantity,
    user=None,
    reference='',
    notes=''
):

    if quantity <= 0:
        raise ValueError(
            'Transfer quantity must be greater than zero.'
        )

    if source_location == destination_location:
        raise ValueError(
            'Source and destination locations must be different.'
        )

    source_stock = Stock.objects.select_for_update().filter(
        business=business,
        product=product,
        location=source_location
    ).first()

    if source_stock is None:
        raise ValueError(
            'There is no stock record at the source location.'
        )

    if source_stock.quantity < quantity:
        raise ValueError(
            'Insufficient stock at the source location.'
        )

    destination_stock, created = (
        Stock.objects.select_for_update().get_or_create(
            business=business,
            product=product,
            location=destination_location,
            defaults={
                'quantity': 0
            }
        )
    )

    source_stock.quantity = F('quantity') - quantity

    source_stock.save(
        update_fields=[
            'quantity',
            'updated_at',
        ]
    )

    destination_stock.quantity = F('quantity') + quantity

    destination_stock.save(
        update_fields=[
            'quantity',
            'updated_at',
        ]
    )

    source_stock.refresh_from_db()
    destination_stock.refresh_from_db()

    StockMovement.objects.create(
        business=business,
        product=product,
        location=source_location,
        movement_type='transfer_out',
        quantity=quantity,
        reference=reference,
        notes=notes,
        created_by=user,
    )

    StockMovement.objects.create(
        business=business,
        product=product,
        location=destination_location,
        movement_type='transfer_in',
        quantity=quantity,
        reference=reference,
        notes=notes,
        created_by=user,
    )