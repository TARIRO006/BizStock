from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User

from businesses.models import Business
from .models import UserProfile
from .forms import RegistrationForm

# Create your views here. 

def register(request):

    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = RegistrationForm(request.POST)

        if form.is_valid():

            # Create the user
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
            )

            # Create the business
            business = Business.objects.create(
                name=form.cleaned_data['business_name'],
                business_type=form.cleaned_data['business_type'],
                phone=form.cleaned_data['phone'],
                address=form.cleaned_data['address'],
                email=form.cleaned_data['email'],
            )

            # Connect user to business
            UserProfile.objects.create(
                user=user,
                business=business
            )

            # Log the user in
            login(request, user)

            return redirect('dashboard')

    else:
        form = RegistrationForm()

    return render(
        request,
        'accounts/register.html',
        {'form': form}
    )


def user_login(request):

    if request.user.is_authenticated:
        return redirect('dashboard')

    error = None

    if request.method == 'POST':

        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)
            return redirect('dashboard')

        error = 'Invalid username or password.'

    return render(
        request,
        'accounts/login.html',
        {'error': error}
    )


def user_logout(request):
    logout(request)
    return redirect('login')