from django.urls import path
from django.contrib import admin
from needy_app import views
urlpatterns = [
    path('',views.needy_home , name='needy_home'),
    path('register/', views.register_needy, name='register_needy'),
    path('login/', views.login_needy, name='login_needy'),
    path('logout/', views.logout_needy, name='logout_needy'),
   
   #button paths
    path('',views.needy_home , name='needy_home'),
    path('login/', views.login_needy, name='login_needy'),
    path('register/', views.register_needy, name='register_needy'),
    path('profile/', views.needy_profile, name='needy_profile'),
    path('request/', views.request_donation, name='request_donation'),
    path('my_requests/', views.my_requests, name='my_requests'),

]