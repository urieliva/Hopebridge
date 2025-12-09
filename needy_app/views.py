from email.policy import default
from django.shortcuts import render, redirect
from .models import NeedyCase
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

def needy_profile(request):
    cases = NeedyCase.objects.filter(needy=request.user).order_by('-date_created')
    return render(request, 'needy/needy_profile.html', {'cases': cases})
def create_case(request):
    if request.method == 'POST':
        title = request.POST['title']
        description = request.POST['description']
        amount_needed = float(request.POST['amount_needed'])

        NeedyCase.objects.create(
            needy=request.user,
            title=title,
            description=description,
            amount_needed=amount_needed,
            amount_raised=0.0,
            is_approved=False
        )
        messages.success(request, 'Case created successfully and is pending approval.')
        return redirect('needy_profile')
    return render(request, 'needy/create_case.html')

def index(request):
    cases = NeedyCase.objects.filter(is_approved=True)
    return render(request, 'index.html', {'cases': cases})
def delete_case(request, case_id):
    case = NeedyCase.objects.get(id=case_id, needy=request.user)
    case.delete()
    messages.success(request, 'Case deleted successfully.')
    return redirect('needy_profile')
def logout_needy(request):
    logout(request)
    return redirect('login_needy')  

@login_required(login_url='login_needy')
def needy_home(request):
    return render(request, 'needy/index.html')

def login_needy(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('needy_home')
        else:
            messages.error(request, 'Invalid username or password.')
            return render(request, 'needy/login.html')
    return render(request, 'needy/login.html')

def register_needy(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')       
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return redirect('register_needy')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken.')
            return redirect('register_needy')

        user = User.objects.create_user(username=username, password=password)
        login(request, user)
        return redirect('needy_home')
    return render(request, 'needy/register.html')

def logout_needy(request):
    logout(request)
    return redirect('login_needy')

@login_required(login_url='login_needy')
def request_donation(request):
        return render(request, 'needy/request_donation.html')

@login_required(login_url='login_needy')
def my_requests(request):
    requests_list=[]
    return render(request, 'needy/my_requests.html', {'requests': requests_list})

@login_required(login_url='login_needy')
def needy_profile(request):
    return render(request, 'needy/profile.html')