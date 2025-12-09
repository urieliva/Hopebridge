from django.urls import path
from . import views

# This is required for namespacing (e.g. {% url 'needy_app:home' %})
app_name = 'needy_app'

urlpatterns = [
    # Dashboard / Home
    path('', views.needy_home, name='home'),
    
    # Authentication
    path('register/', views.register_needy, name='register_needy'),
    path('login/', views.login_needy, name='login_needy'),
    path('logout/', views.logout_needy, name='logout_needy'),

    # Profile & Requests
    path('profile/', views.needy_profile, name='needy_profile'),
    
    # Case Management 
    # (I mapped 'request' to the create_case view we defined earlier)
    path('request/', views.create_case, name='create_case'),
    path('delete/<int:case_id>/', views.delete_case, name='delete_case'),
]