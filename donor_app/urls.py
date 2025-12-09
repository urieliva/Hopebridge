from django.urls import path
from . import views

app_name = 'donor_app'

urlpatterns = [
    # Landing Page: localhost:8000/donor/
    path('', views.index, name='home'),
    
    # Authentication
    path('login/', views.login_donor, name='login_donor'),
    path('register/', views.register_donor, name='register_donor'),
    path('logout/', views.logout_donor, name='logout_donor'),
    
    # User Profile
    path('profile/', views.donor_profile, name='donor_profile'),
    
    # Donation Logic
    # This URL must capture the case_id to pass to the view
    path('donate/<int:case_id>/', views.donate, name='donate'),
    
    # M-Pesa Payment Page
    path('mpesa/pay/', views.lipa_na_mpesa, name='lipa_na_mpesa'),
    
    # Donation History
    # ... existing paths ...
    path('donor/', views.donor_dashboard, name='donor_dashboard'),
    
    # ADD THIS NEW PATH:
    path('donation_history/', views.donation_history_view, name='donation_history'), 
]