from django.urls import path
from . import views

from .import views
urlpatterns = [
    path('', views.donor_home, name='donor_home'),
    path('',views.index, name='index'),
    path('login/', views.login_donor, name='login_donor'),
    path('register/', views.register_donor, name='register_donor'),
    path('logout/', views.logout_donor, name='logout_donor'),
    path('donate/', views.index, name='index'),
    path('profile/', views.donor_profile, name='donor_profile'),
    path('mpesa_callback/', views.lipa_na_mpesa, name='mpesa_callback'),
    path('donate/', views.donate, name='donate'),
]