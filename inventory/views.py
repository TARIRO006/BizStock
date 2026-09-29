from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from .models import Product, Category
from .forms import ProductForm, CategoryForm


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