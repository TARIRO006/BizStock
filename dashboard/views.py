from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from datetime import date, timedelta
from decimal import Decimal
from django.db.models import Sum
from django.utils import timezone
from inventory.models import Product, Sale
from shops.models import Location, Stock
import json

# Create your views here.

@login_required
def dashboard(request):
    business = request.user.userprofile.business
    today = timezone.localdate()

    # Reporting period selected by the user.
    
    period = request.GET.get('period', '7')
    if period not in {'today', '7', '30', 'all', 'custom'}:
        period = '7'

    start_date = None
    end_date = None

    if period == 'custom':
        start_date_input = request.GET.get('start_date', '')
        end_date_input = request.GET.get('end_date', '')

        try:
            start_date = date.fromisoformat(start_date_input)
            end_date = date.fromisoformat(end_date_input)

            if start_date > end_date:
                start_date = None
                end_date = None
        except (ValueError, TypeError):
            start_date = None
            end_date = None


    sales = (
        Sale.objects.filter(
            business=business,
            status='completed',
        )
        .select_related('location')
        .prefetch_related('items')
    )

    
    if period == 'today':
        sales = sales.filter(completed_at__date=today)

    elif period in {'7', '30'}:
        start_date = today - timedelta(days=int(period) - 1)
        end_date = today

        sales = sales.filter(
            completed_at__date__gte=start_date,
            completed_at__date__lte=end_date
        )

    elif period == 'custom':
        if start_date and end_date:
            sales = sales.filter(
                completed_at__date__gte=start_date,
                completed_at__date__lte=end_date
            )
        else:
            # Invalid or incomplete dates: return no sales.
            sales = sales.none()

    # Calculate revenue and product cost for the selected period.
    total_revenue = Decimal('0.00')
    total_cost = Decimal('0.00')
    shop_totals = {}

    for sale in sales:
        shop_id = sale.location_id
        is_shop_sale = sale.location.location_type == 'shop'

        if is_shop_sale:
            if shop_id not in shop_totals:
                shop_totals[shop_id] = {
                    'name': sale.location.name,
                    'revenue': Decimal('0.00'),
                    'cost': Decimal('0.00'),
                    'gross_profit': Decimal('0.00'),
                    'sales_count': 0,
                    'revenue_percentage': Decimal('0.00'),
                }

            # Count each completed sale once, not once per product.
            shop_totals[shop_id]['sales_count'] += 1

        for item in sale.items.all():
            total_revenue += item.line_total
            total_cost += item.line_cost

            if is_shop_sale:
                shop_totals[shop_id]['revenue'] += item.line_total
                shop_totals[shop_id]['cost'] += item.line_cost

    gross_profit = total_revenue - total_cost

    # Calculate shop profit and each shop's share of shop revenue.
    shop_revenue_total = sum(
        (shop['revenue'] for shop in shop_totals.values()),
        start=Decimal('0.00'),
    )

    for shop in shop_totals.values():
        shop['gross_profit'] = shop['revenue'] - shop['cost']

        if shop_revenue_total > 0:
            shop['revenue_percentage'] = (
                shop['revenue'] / shop_revenue_total
            ) * Decimal('100.00')

    top_shops = sorted(
        shop_totals.values(),
        key=lambda shop: shop['revenue'],
        reverse=True,
    )

    gross_profit = total_revenue - total_cost

    # Prepare daily revenue for the sales trend chart.
    daily_revenue = {}

    for sale in sales:
        if sale.completed_at:
            sale_date = sale.completed_at.date()

            sale_revenue = sum(
                (item.line_total for item in sale.items.all()),
                start=Decimal('0.00'),
            )

            daily_revenue[sale_date] = (
                daily_revenue.get(sale_date, Decimal('0.00'))
                + sale_revenue
            )

    # Determine the first date shown on the chart.
    if period == 'today':
        chart_start_date = today

    elif period in {'7', '30'}:
        chart_start_date = today - timedelta(days=int(period) - 1)

    elif period == 'custom' and start_date and end_date:
        chart_start_date = start_date

    else:
        chart_start_date = (
            min(daily_revenue) if daily_revenue else today
        )

    chart_end_date = end_date if period == 'custom' and end_date else today

    chart_dates = []
    current_date = chart_start_date

    while current_date <= chart_end_date:
        chart_dates.append(current_date)
        current_date += timedelta(days=1)

    chart_labels = [d.strftime('%d %b') for d in chart_dates]
    chart_values = [
        float(daily_revenue.get(d, Decimal('0.00')))
        for d in chart_dates
    ]


    # Calculate today's sales revenue independently of the selected period.
    todays_sales = Sale.objects.filter(
        business=business,
        status='completed',
        completed_at__date=today,
    ).prefetch_related('items')

    todays_revenue = Decimal('0.00')

    for sale in todays_sales:
        for item in sale.items.all():
            todays_revenue += item.line_total

    # Active products and shops for this business.
    products = Product.objects.filter(
        business=business,
        is_active=True,
    )

    product_count = products.count()

    active_shops = Location.objects.filter(
        business=business,
        location_type='shop',
        is_active=True,
    )

    shop_count = active_shops.count()

    # Sum stock across this business's active locations.
    stock_totals = dict(
        Stock.objects.filter(
            business=business,
            location__business=business,
            location__is_active=True,
            product__business=business,
        )
        .values('product_id')
        .annotate(total_quantity=Sum('quantity'))
        .values_list('product_id', 'total_quantity')
    )

    low_stock_items = []

    for product in products:
        quantity = stock_totals.get(product.pk)

        if quantity is None:
            quantity = Decimal('0.00')

        if quantity <= product.minimum_stock:
            low_stock_items.append({
                'product': product,
                'quantity': quantity,
            })

    low_stock_items.sort(key=lambda item: item['quantity'])

    top_shops = sorted(
        shop_totals.values(),
        key=lambda shop: shop['revenue'],
        reverse=True,
    )

    context = {
        'business': business,
        'today': today,
        'period': period,
        'total_revenue': total_revenue,
        'total_cost': total_cost,
        'gross_profit': gross_profit,
        'todays_revenue': todays_revenue,
        'completed_sales_count': sales.count(),
        'product_count': product_count,
        'shop_count': shop_count,
        'low_stock_items': low_stock_items,
        'low_stock_count': len(low_stock_items),
        'top_shops': top_shops,
        'chart_labels': chart_labels,
        'chart_values': chart_values,
        'start_date': start_date,
        'end_date': end_date,
    }

    return render(
        request,
        'dashboard/dashboard.html',
        context,
    )


@login_required
def dashboard_home(request):
    business = request.user.userprofile.business
    today = timezone.localdate()

    # Choose a reporting period.
    period = request.GET.get('period', '30')
    if period not in {'today', '7', '30', 'all'}:
        period = '30'

    sales = Sale.objects.filter(
        business=business,
        status='completed',
    ).prefetch_related('items', 'location')

    if period == 'today':
        sales = sales.filter(completed_at__date=today)
    elif period in {'7', '30'}:
        days = int(period)
        start_date = today - timedelta(days=days - 1)
        sales = sales.filter(
            completed_at__date__gte=start_date,
            completed_at__date__lte=today,
        )

    # Calculate revenue, product cost and gross profit.
    total_revenue = Decimal('0.00')
    total_cost = Decimal('0.00')
    completed_sales_count = sales.count()
    shop_totals = {}

    for sale in sales:
        for item in sale.items.all():
            total_revenue += item.line_total
            total_cost += item.line_cost

            shop_id = sale.location_id
            if shop_id not in shop_totals:
                shop_totals[shop_id] = {
                    'name': sale.location.name,
                    'revenue': Decimal('0.00'),
                }

            shop_totals[shop_id]['revenue'] += item.line_total

    gross_profit = total_revenue - total_cost

    # Products belonging to this business.
    products = Product.objects.filter(
        business=business,
        is_active=True,
    )
    product_count = products.count()

    # Sum each product's stock across the business's locations.
    stock_totals = dict(
        Stock.objects.filter(
            business=business,
            location__business=business,
        )
        .values('product_id')
        .annotate(total_quantity=Sum('quantity'))
        .values_list('product_id', 'total_quantity')
    )

    low_stock_items = []
    for product in products:
        quantity = stock_totals.get(product.pk) or Decimal('0.00')
        if quantity <= product.minimum_stock:
            low_stock_items.append({
                'product': product,
                'quantity': quantity,
            })

    low_stock_items.sort(key=lambda item: item['quantity'])
    top_shops = sorted(
        shop_totals.values(),
        key=lambda shop: shop['revenue'],
        reverse=True,
    )

    context = {
        'period': period,
        'today': today,
        'total_revenue': total_revenue,
        'total_cost': total_cost,
        'gross_profit': gross_profit,
        'completed_sales_count': completed_sales_count,
        'product_count': product_count,
        'low_stock_items': low_stock_items,
        'low_stock_count': len(low_stock_items),
        'top_shops': top_shops,
    }

    return render(request, 'dashboard/home.html', context)
