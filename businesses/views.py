from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages

from .forms import BusinessSettingsForm

# Create your views here.

@login_required
def settings_home(request):
    return render(request, 'businesses/settings_home.html')


@login_required
def business_settings(request):

    business = request.user.userprofile.business

    if request.method == 'POST':
        form = BusinessSettingsForm(
            request.POST,
            request.FILES,
            instance=business
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                'Business settings updated successfully!'
            )

            return redirect('business_settings')

    else:
        form = BusinessSettingsForm(instance=business)

    return render(
        request,
        'businesses/business_settings.html',
        {
            'form': form,
            'business': business,
        }
    )
