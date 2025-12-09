from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Donation
from needy_app.models import NeedyCase
import requests
from django.conf import settings
from django.shortcuts import redirect, render
from django.http import JsonResponse
from datetime import datetime
import base64
from django.http import JsonResponse
from .mpesa import lipa_na_mpesa

def donate(request):
    if request.method == "POST":
        phone = request.POST.get('phone')        # e.g., 2547XXXXXXXX
        amount = request.POST.get('amount')      # e.g., 100
        response = lipa_na_mpesa(phone, amount)
        return JsonResponse(response)
    
def get_access_token():
    consumer_key = settings.MPESA_CONSUMER_KEY
    consumer_secret = settings.MPESA_CONSUMER_SECRET
    api_url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    r = requests.get(api_url, auth=(consumer_key, consumer_secret))
    return r.json()['access_token']


def lipa_na_mpesa(request):
    if request.method == "POST":
        phone = request.POST.get("phone")
        amount = request.POST.get("amount")

        access_token = get_access_token()
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

        password_str = settings.MPESA_SHORTCODE + settings.MPESA_PASSKEY + timestamp
        password = base64.b64encode(password_str.encode()).decode()

        stk_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"

        headers = {"Authorization": f"Bearer {access_token}"}

        payload = {
            "BusinessShortCode": settings.MPESA_SHORTCODE,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": amount,
            "PartyA": phone,
            "PartyB": settings.MPESA_SHORTCODE,
            "PhoneNumber": phone,
            "CallBackURL": settings.MPESA_CALLBACK_URL,
            "AccountReference": "HopeBridgeDonation",
            "TransactionDesc": "Donation Payment"
        }

        response = requests.post(stk_url, json=payload, headers=headers)

        return JsonResponse(response.json())

    return render(request, "donor/mpesa_payment.html")

@login_required(login_url='login_donor')
def donor_home(request):
    return render(request, 'donor/index.html')


def login_donor(request):
    if request.user.is_authenticated:
        return redirect('donor_home')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('donor_home')
        else:
            messages.error(request, 'Invalid username or password')

    return render(request, 'donor/login.html')


def register_donor(request):
    if request.user.is_authenticated:
        return redirect('donor_home')

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 != password2:
            messages.error(request, "Passwords do not match")
            return redirect('register_donor')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect('register_donor')

        user = User.objects.create_user(username=username, email=email, password=password1)
        user.save()
        messages.success(request, "Account created successfully. Please login.")
        return redirect('login_donor')

    return render(request, 'donor/register.html')


def logout_donor(request):
    logout(request)
    return redirect('login_donor')

@login_required(login_url='login_donor')
def donate(request, case_id):
    case = NeedyCase.objects.get(id=case_id)

    if request.method == 'POST':
        amount = float(request.POST['amount'])
        Donation.objects.create(
            donor=request.user,
            case=case,
            amount=amount
        )

        case.amount_raised += amount
        case.save()

        return render(request, 'donor/success.html', {'case': case})
    return render(request, 'donor/donate.html', {'case': case})
def index(request):     
        cases = NeedyCase.objects.filter(is_approved=True)
        return render(request, 'donor/index.html', {'cases': cases})
def donor_profile(request):
    donations = Donation.objects.filter(donor=request.user).order_by('-date')
    total_donated = sum(donation.amount for donation in donations)
    return render(request, 'donor/donor_profile.html', {'donations': donations, 'total_donated': total_donated})

