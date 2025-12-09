from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import NeedyCase

# ==========================================
#  DASHBOARD & PROFILE
# ==========================================

@login_required(login_url='needy_app:login_needy')
def needy_home(request):
    """Main Dashboard"""
    return render(request, 'needy/index.html')

@login_required(login_url='needy_app:login_needy')
def needy_profile(request):
    """
    Profile Page: Handles updating details AND showing history.
    """
    # 1. HANDLE SAVING DATA (If user clicked "Save Changes")
    if request.method == 'POST':
        email = request.POST.get('email')
        
        # Update the user's email
        user = request.user
        user.email = email
        user.save()
        
        messages.success(request, 'Profile details saved successfully!')
        return redirect('needy_app:needy_profile')

    # 2. LOAD PAGE (Standard view)
    # Filter cases so the user ONLY sees their own requests
    cases = NeedyCase.objects.filter(needy=request.user).order_by('-date_created')
    
    return render(request, 'needy/profile.html', {'cases': cases})

# ==========================================
#  CASE MANAGEMENT (Create / Delete)
# ==========================================

@login_required(login_url='needy_app:login_needy')
def create_case(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        amount_needed = request.POST.get('amount_needed')

        # Create the case linked to the current user
        NeedyCase.objects.create(
            needy=request.user,
            title=title,
            description=description,
            amount_needed=float(amount_needed),
            amount_raised=0.0,
            is_approved=False
        )
        messages.success(request, 'Case created successfully and is pending approval.')
        
        # Redirect to Profile to see the new case in history
        return redirect('needy_app:needy_profile')

    return render(request, 'needy/create_case.html')

@login_required(login_url='needy_app:login_needy')
def delete_case(request, case_id):
    # Use get_object_or_404 for safety
    case = get_object_or_404(NeedyCase, id=case_id, needy=request.user)
    
    case.delete()
    messages.success(request, 'Case deleted successfully.')
    return redirect('needy_app:needy_profile')

# ==========================================
#  AUTHENTICATION
# ==========================================

def login_needy(request):
    if request.user.is_authenticated:
        return redirect('needy_app:home') 

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('needy_app:home')
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'needy/login.html')

def register_needy(request):
    if request.user.is_authenticated:
        return redirect('needy_app:home')

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')        
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return redirect('needy_app:register_needy')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken.')
            return redirect('needy_app:register_needy')

        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        
        # Log them in automatically
        login(request, user)
        messages.success(request, "Account created successfully!")
        return redirect('needy_app:home')

    return render(request, 'needy/register.html')

def logout_needy(request):
    logout(request)
    return redirect('needy_app:login_needy')