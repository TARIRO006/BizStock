from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Stock
from .models import Stock, Location, StockMovement
from .forms import LocationForm, StockForm, StockTransferForm
from django.contrib import messages
from .services import transfer_stock

# Create your views here.

@login_required
def stock_list(request):

    business = request.user.userprofile.business

    stock_records = Stock.objects.filter(
        business=business,
        location__is_active=True
    ).select_related(
        'product',
        'location'
    )

    return render(
        request,
        'shops/stock_list.html',
        {
            'stock_records': stock_records,
        }
    )


@login_required
def location_list(request):

    business = request.user.userprofile.business

    locations = Location.objects.filter(
        business=business
    )

    return render(
        request,
        'shops/location_list.html',
        {
            'locations': locations,
        }
    )


@login_required
def location_create(request):

    business = request.user.userprofile.business

    if request.method == 'POST':

        form = LocationForm(request.POST)

        if form.is_valid():

            location = form.save(commit=False)

            location.business = business

            location.save()

            return redirect('location_list')

    else:

        form = LocationForm()

    return render(
        request,
        'shops/location_form.html',
        {
            'form': form,
        }
    )


@login_required
def location_edit(request, location_id):

    business = request.user.userprofile.business

    location = get_object_or_404(
        Location,
        id=location_id,
        business=business
    )

    if request.method == 'POST':

        form = LocationForm(
            request.POST,
            instance=location
        )

        if form.is_valid():

            form.save()

            return redirect('location_list')

    else:

        form = LocationForm(
            instance=location
        )

    return render(
        request,
        'shops/location_form.html',
        {
            'form': form,
            'editing': True,
            'location': location,
        }
    )


@login_required
def stock_create(request):

    business = request.user.userprofile.business

    if request.method == 'POST':

        form = StockForm(
            request.POST,
            business=business
        )

        if form.is_valid():

            stock = form.save(commit=False)

            stock.business = business

            stock.save()

            return redirect('stock_list')

    else:

        form = StockForm(
            business=business
        )

    return render(
        request,
        'shops/stock_form.html',
        {
            'form': form,
        }
    )


@login_required
def movement_list(request):

    business = request.user.userprofile.business

    movements = StockMovement.objects.filter(
        business=business
    ).select_related(
        'product',
        'location',
        'created_by'
    )

    return render(
        request,
        'shops/movement_list.html',
        {
            'movements': movements,
        }
    )


@login_required
def stock_transfer(request):

    business = request.user.userprofile.business

    if request.method == 'POST':

        form = StockTransferForm(
            request.POST,
            business=business
        )

        if form.is_valid():

            try:

                transfer_stock(
                    business=business,
                    product=form.cleaned_data['product'],
                    source_location=form.cleaned_data['source_location'],
                    destination_location=form.cleaned_data['destination_location'],
                    quantity=form.cleaned_data['quantity'],
                    user=request.user,
                    reference=form.cleaned_data['reference'],
                    notes=form.cleaned_data['notes'],
                )

            except ValueError as error:

                form.add_error(
                    None,
                    str(error)
                )

            else:

                messages.success(
                    request,
                    'Stock transferred successfully.'
                )

                return redirect('stock_list')

    else:

        form = StockTransferForm(
            business=business
        )

    return render(
        request,
        'shops/stock_transfer.html',
        {
            'form': form,
        }
    )