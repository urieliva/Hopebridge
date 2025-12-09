from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.conf import settings
import requests
import base64
from datetime import datetime

# Import models
from .models import Donation
from needy_app.models import NeedyCase

# ===========================
# M-PESA HELPER FUNCTIONS
# ===========================

def get_access_token():
    """Generates M-Pesa Access Token"""
    consumer_key = settings.MPESA_CONSUMER_KEY
    consumer_secret = settings.MPESA_CONSUMER_SECRET
    api_url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    
    try:
        r = requests.get(api_url, auth=(consumer_key, consumer_secret))
        r.raise_for_status() # Check for HTTP errors
        return r.json()['access_token']
    except Exception as e:
        print(f"Error generating token: {e}")
        return None

def lipa_na_mpesa(request):
    """View to trigger STK Push"""
    if request.method == "POST":
        phone = request.POST.get("phone")
        amount = request.POST.get("amount")
        
        access_token = get_access_token()
        if not access_token:
            return JsonResponse({'error': 'Failed to get access token'}, status=500)

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

        try:
            response = requests.post(stk_url, json=payload, headers=headers)
            return JsonResponse(response.json())
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return render(request, "donor/mpesa_payment.html")

# ===========================
# DONOR VIEWS
# ===========================

def index(request):      
    """Public landing page or dashboard"""
    cases = NeedyCase.objects.filter(is_approved=True)
    return render(request, 'donor/index.html', {'cases': cases})

@login_required(login_url='donor_app:login_donor')
def donor_home(request):
    """Dashboard specifically for logged-in donors"""
    cases = NeedyCase.objects.filter(is_approved=True)
    return render(request, 'donor/index.html', {'cases': cases})

@login_required(login_url='donor_app:login_donor')
def donate(request, case_id):
    """Process donation for a specific case"""
    case = get_object_or_404(NeedyCase, id=case_id)

    if request.method == 'POST':
        try:
            amount = float(request.POST.get('amount', 0))
            if amount > 0:
                # 1. Save to DB
                Donation.objects.create(
                    donor=request.user,
                    case=case,
                    amount=amount
                )
                
                # 2. Update Case Total
                case.amount_raised += amount
                case.save()

                # 3. Trigger M-Pesa (Optional: You might want to do this via JS or redirect)
                # For now, we just show success
                messages.success(request, f"Successfully donated KES {amount}")
                return render(request, 'donor/success.html', {'case': case})
        except ValueError:
             messages.error(request, "Invalid amount entered.")

    return render(request, 'donor/donate.html', {'case': case})

@login_required(login_url='donor_app:login_donor')
def donor_profile(request):
    donations = Donation.objects.filter(donor=request.user).order_by('-date')
    total_donated = sum(donation.amount for donation in donations)
    return render(request, 'donor/donor_profile.html', {'donations': donations, 'total_donated': total_donated})

# ===========================
# AUTHENTICATION
# ===========================

def login_donor(request):
    if request.user.is_authenticated:
        return redirect('donor_app:home') # Updated namespace

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('donor_app:home') # Updated namespace
        else:
            messages.error(request, 'Invalid username or password')

    return render(request, 'donor/login.html')

def register_donor(request):
    if request.user.is_authenticated:
        return redirect('donor_app:home')

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 != password2:
            messages.error(request, "Passwords do not match")
            return redirect('donor_app:register_donor')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect('donor_app:register_donor')

        user = User.objects.create_user(username=username, email=email, password=password1)
        user.save()
        messages.success(request, "Account created successfully. Please login.")
        return redirect('donor_app:login_donor')

    return render(request, 'donor/register.html')

def logout_donor(request):
    logout(request)
    return redirect('donor_app:login_donor')


def donation_history_view(request):
    # 1. (Security Check) Ensure user is logged in
    if not request.user.is_authenticated:
        return redirect('login') 

    # 2. (Database Query Placeholder) Replace this with actual database code
    # Example data:
    donations = [
        {'amount': 5000, 'date': '2025-11-01', 'project': 'Project Feed 1000'},
        {'amount': 10000, 'date': '2025-10-15', 'project': 'Health Clinic Fund'},
    ]
    
    context = {
        'donations': donations,
        'total_donated': sum(d['amount'] for d in donations)
    }
    
    # 3. Tell the server to display the template file
    return render(request, 'donor/donation_history.html', context)

def donor_dashboard(request):
    # This is where your logic for fetching stats/data goes
    # Example:
    context = {
        'total_donated': 20000,
        'lives_impacted': 15,
        # ... other context variables
    }
    return render(request, 'donor_dashboard.html', context)
    
# ... other view functions like donation_history_view ...
def donation_history_view(request):
    # 1. (Security Check) Ensure user is logged in
    if not request.user.is_authenticated:
        return redirect('login') 

    # 2. (Database Query Placeholder) Replace this with actual database code
    # Example data:
    donations = [
        {'amount': 5000, 'date': '2025-11-01', 'project': 'Project Feed 1000'},
        {'amount': 10000, 'date': '2025-10-15', 'project': 'Health Clinic Fund'},
    ]
    
    context = {
        'donations': donations,
        'total_donated': sum(d['amount'] for d in donations)
    }
    
    # 3. Tell the server to display the template file
    return render(request, 'donor/donation_history.html', context)
 