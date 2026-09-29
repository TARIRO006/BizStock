from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Stock

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