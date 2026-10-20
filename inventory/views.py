from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from .services import receive_purchase, complete_sale
from django.db.models import Sum, Count, Q, F, DecimalField, ExpressionWrapper
from django.db.models.functions import Coalesce
from decimal import Decimal
from django.views.decorators.http import require_POST


from .models import Product, Category, Supplier,  Purchase, Sale, SaleItem
from .forms import ProductForm, CategoryForm, SupplierForm, PurchaseForm, PurchaseItemFormSet, SaleForm, SaleItemFormSet


@login_required
def product_list(request):

    business = request.user.userprofile.business

    products = Product.objects.filter(
        business=business
    ).select_related('category')

    categories = Category.objects.filter(
        business=business
    )

    context = {
        'products': products,
        'categories': categories,
    }

    return render(
        request,
        'inventory/product_list.html',
        context
    )


@login_required
def product_create(request):

    business = request.user.userprofile.business

    if request.method == 'POST':

        form = ProductForm(
            request.POST,
            business=business
        )

        if form.is_valid():

            product = form.save(
                commit=False
            )

            product.business = business

            product.save()

            return redirect('product_list')

    else:

        form = ProductForm(
            business=business
        )

    context = {
        'form': form,
    }

    return render(
        request,
        'inventory/product_form.html',
        context
    )


@login_required
def category_list(request):

    business = request.user.userprofile.business

    categories = Category.objects.filter(
        business=business
    ).prefetch_related('products')

    return render(
        request,
        'inventory/category_list.html',
        {
            'categories': categories,
        }
    )


@login_required
def category_create(request):

    business = request.user.userprofile.business

    if request.method == 'POST':

        form = CategoryForm(request.POST)

        if form.is_valid():

            category = form.save(
                commit=False
            )

            category.business = business

            category.save()

            return redirect('category_list')

    else:

        form = CategoryForm()

    return render(
        request,
        'inventory/category_form.html',
        {
            'form': form,
        }
    )


@login_required
def product_edit(request, product_id):

    business = request.user.userprofile.business

    product = Product.objects.get(
        id=product_id,
        business=business
    )

    if request.method == 'POST':

        form = ProductForm(
            request.POST,
            instance=product,
            business=business
        )

        if form.is_valid():
            form.save()

            return redirect('product_list')

    else:

        form = ProductForm(
            instance=product,
            business=business
        )

    return render(
        request,
        'inventory/product_form.html',
        {
            'form': form,
            'editing': True,
            'product': product,
        }
    )


@login_required
def product_delete(request, product_id):

    business = request.user.userprofile.business

    product = Product.objects.get(
        id=product_id,
        business=business
    )

    if request.method == 'POST':

        product.delete()

        return redirect('product_list')

    return render(
        request,
        'inventory/product_confirm_delete.html',
        {
            'product': product,
        }
    )


@login_required
def category_edit(request, category_id):

    business = request.user.userprofile.business

    category = Category.objects.get(
        id=category_id,
        business=business
    )

    if request.method == 'POST':

        form = CategoryForm(
            request.POST,
            instance=category
        )

        if form.is_valid():

            form.save()

            return redirect('category_list')

    else:

        form = CategoryForm(
            instance=category
        )

    return render(
        request,
        'inventory/category_form.html',
        {
            'form': form,
            'editing': True,
            'category': category,
        }
    )


@login_required
def category_delete(request, category_id):

    business = request.user.userprofile.business

    category = Category.objects.get(
        id=category_id,
        business=business
    )

    if request.method == 'POST':

        category.delete()

        return redirect('category_list')

    return render(
        request,
        'inventory/category_confirm_delete.html',
        {
            'category': category,
        }
    )



@login_required
def supplier_list(request):

    business = request.user.userprofile.business

    suppliers = Supplier.objects.filter(
        business=business
    )

    return render(
        request,
        'inventory/supplier_list.html',
        {'suppliers': suppliers}
    )


@login_required
def supplier_create(request):

    business = request.user.userprofile.business

    if request.method == 'POST':
        form = SupplierForm(request.POST)

        if form.is_valid():
            supplier = form.save(commit=False)
            supplier.business = business
            supplier.save()

            return redirect('supplier_list')
    else:
        form = SupplierForm()

    return render(
        request,
        'inventory/supplier_form.html',
        {'form': form}
    )


@login_required
def supplier_edit(request, supplier_id):

    business = request.user.userprofile.business

    supplier = get_object_or_404(
        Supplier,
        id=supplier_id,
        business=business
    )

    if request.method == 'POST':
        form = SupplierForm(
            request.POST,
            instance=supplier
        )

        if form.is_valid():
            form.save()
            return redirect('supplier_list')
    else:
        form = SupplierForm(instance=supplier)

    return render(
        request,
        'inventory/supplier_form.html',
        {
            'form': form,
            'editing': True,
            'supplier': supplier,
        }
    )



@login_required
def purchase_create(request):
    business = request.user.userprofile.business

    purchase = Purchase(business=business)

    if request.method == 'POST':
        form = PurchaseForm(
            request.POST,
            instance=purchase,
            business=business,
        )

        formset = PurchaseItemFormSet(
            request.POST,
            instance=purchase,
            form_kwargs={'business': business},
        )

        if form.is_valid() and formset.is_valid():
            items_to_save = [
            item_form
            for item_form in formset.forms
            if item_form.cleaned_data
            and not item_form.cleaned_data.get('DELETE', False)
            and item_form.cleaned_data.get('product')
            ]

            if not items_to_save:
                messages.error(
                    request,
                    'Add at least one product to the purchase.',
                )
            else:
                with transaction.atomic():
                    purchase = form.save(commit=False)
                    purchase.business = business
                    purchase.created_by = request.user
                    purchase.status = 'draft'
                    purchase.save()

                    formset.instance = purchase
                    formset.save(commit=False)

                    for item in formset.deleted_objects:
                        item.delete()

                    for item in formset.save(commit=False):
                        item.purchase = purchase
                        item.save()

                messages.success(
                    request,
                    'Purchase saved as a draft.',
                )
                return redirect('purchase_list')
    else:
        form = PurchaseForm(
            instance=purchase,
            business=business,
        )
        formset = PurchaseItemFormSet(
            instance=purchase,
            form_kwargs={'business': business},
        )

    return render(
        request,
        'inventory/purchase_form.html',
        {
            'form': form,
            'formset': formset,
        },
    )



@login_required
def purchase_list(request):
    business = request.user.userprofile.business

    purchases = (
        Purchase.objects
        .filter(business=business)
        .select_related('supplier', 'location')
        .prefetch_related('items__product')
        .order_by('-created_at')
    )

    return render(
        request,
        'inventory/purchase_list.html',
        {
            'purchases': purchases,
        },
    )



@login_required
def purchase_receive(request, purchase_id):
    if request.method != 'POST':
        return redirect('purchase_list')

    business = request.user.userprofile.business

    try:
        purchase = receive_purchase(
            purchase_id=purchase_id,
            business=business,
            user=request.user,
        )
    except Purchase.DoesNotExist:
        messages.error(request, 'Purchase not found.')
        return redirect('purchase_list')
    except ValueError as error:
        messages.error(request, str(error))
        return redirect('purchase_list')

    messages.success(
        request,
        f'Purchase {purchase.reference or purchase.pk} received successfully. Stock has been updated.',
    )

    return redirect('purchase_list')



@login_required
def purchase_detail(request, purchase_id):
    business = request.user.userprofile.business

    purchase = get_object_or_404(
        Purchase.objects.select_related(
            'supplier',
            'location',
            'created_by',
        ).prefetch_related('items__product'),
        id=purchase_id,
        business=business,
    )

    return render(
        request,
        'inventory/purchase_detail.html',
        {
            'purchase': purchase,
            'items': purchase.items.all(),
        },
    )



@login_required
def purchase_cancel(request, purchase_id):
    if request.method != 'POST':
        return redirect('purchase_list')

    business = request.user.userprofile.business

    purchase = get_object_or_404(
        Purchase,
        id=purchase_id,
        business=business,
    )

    if purchase.status != 'draft':
        messages.error(
            request,
            'Only draft purchases can be cancelled.',
        )
        return redirect(
            'purchase_detail',
            purchase_id=purchase.id,
        )

    purchase.status = 'cancelled'
    purchase.save(update_fields=['status'])

    messages.success(
        request,
        f'Purchase {purchase.reference or purchase.pk} was cancelled.',
    )

    return redirect(
        'purchase_detail',
        purchase_id=purchase.id,
    )



@login_required
def purchase_reports(request):
    business = request.user.userprofile.business

    received_purchases = (
        Purchase.objects
        .filter(business=business, status='received')
        .select_related('supplier', 'location')
        .prefetch_related('items')
        .order_by('-received_at')
    )

    line_total_expression = ExpressionWrapper(
        F('items__quantity') * F('items__unit_cost'),
        output_field=DecimalField(max_digits=24, decimal_places=2),
    )

    spending = received_purchases.aggregate(
        total=Sum(line_total_expression)
    )['total'] or Decimal('0.00')

    received_count = Purchase.objects.filter(
        business=business,
        status='received',
    ).count()

    draft_count = Purchase.objects.filter(
        business=business,
        status='draft',
    ).count()

    # Group spending by supplier.
    supplier_spending = (
        Purchase.objects
        .filter(business=business, status='received')
        .values('supplier_id', 'supplier__name')
        .annotate(
            total_spending=Sum(line_total_expression),
            purchase_count=Count('id', distinct=True),
        )
        .order_by('-total_spending')
    )

    context = {
        'total_spending': spending,
        'received_count': received_count,
        'draft_count': draft_count,
        'supplier_spending': supplier_spending,
        'received_purchases': received_purchases,
    }

    return render(
        request,
        'inventory/purchase_reports.html',
        context,
    )



@login_required
def sale_create(request):
    business = request.user.userprofile.business
    sale = Sale(business=business)

    if request.method == 'POST':
        form = SaleForm(
            request.POST,
            instance=sale,
            business=business,
        )

        formset = SaleItemFormSet(
            request.POST,
            instance=sale,
            form_kwargs={'business': business},
        )

        if form.is_valid() and formset.is_valid():
            item_forms = [
                item_form
                for item_form in formset.forms
                if item_form.cleaned_data
                and not item_form.cleaned_data.get('DELETE', False)
                and item_form.cleaned_data.get('product')
            ]

            if not item_forms:
                messages.error(
                    request,
                    'Add at least one product to the sale.',
                )
            else:
                with transaction.atomic():
                    sale = form.save(commit=False)
                    sale.business = business
                    sale.created_by = request.user
                    sale.status = 'draft'
                    sale.save()

                    formset.instance = sale
                    items = formset.save(commit=False)

                    for item in items:
                        item.sale = sale
                        item.unit_cost = item.product.cost_price
                        item.save()

                    formset.save_m2m()

                messages.success(
                    request,
                    'Sale saved as a draft. Stock has not changed.',
                )
                return redirect('sale_list')
    else:
        form = SaleForm(business=business)
        formset = SaleItemFormSet(
            instance=sale,
            form_kwargs={'business': business},
        )

    return render(
        request,
        'inventory/sale_form.html',
        {
            'form': form,
            'formset': formset,
        },
    )




@login_required
def sale_list(request):
    business = request.user.userprofile.business

    sales = (
        Sale.objects
        .filter(business=business)
        .select_related('location', 'created_by')
        .prefetch_related('items__product')
        .order_by('-created_at')
    )

    return render(
        request,
        'inventory/sale_list.html',
        {'sales': sales},
    )



@login_required
@require_POST
def sale_complete(request, sale_id):
    business = request.user.userprofile.business

    try:
        sale = complete_sale(
            sale_id=sale_id,
            business=business,
            user=request.user,
        )
    except Sale.DoesNotExist:
        messages.error(request, 'Sale not found.')
        return redirect('sale_list')
    except ValueError as error:
        messages.error(request, str(error))
        return redirect('sale_list')

    messages.success(
        request,
        f'Sale {sale.reference or "#" + str(sale.pk)} completed successfully. '
        'Stock has been updated.',
    )
    return redirect('sale_list')



@login_required
def sale_detail(request, sale_id):
    business = request.user.userprofile.business

    sale = get_object_or_404(
        Sale.objects.filter(business=business)
        .select_related('location', 'created_by')
        .prefetch_related('items__product'),
        pk=sale_id,
    )

    return render(
        request,
        'inventory/sale_detail.html',
        {'sale': sale},
    )
