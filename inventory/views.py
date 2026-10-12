from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction

from .models import Product, Category, Supplier,  Purchase
from .forms import ProductForm, CategoryForm, SupplierForm, PurchaseForm, PurchaseItemFormSet


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

