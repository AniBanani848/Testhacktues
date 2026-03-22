from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('verify-email/', views.verify_email, name='verify_email'),
    path('verify-email/resend/', views.resend_verification, name='resend_verification'),
    path('register/', views.register, name='register'),
    path(
        'login/',
        auth_views.LoginView.as_view(template_name='login.html'),
        name='login',
    ),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('resources/', views.resource_list, name='resource_list'),
    path('resources/add/', views.add_resource, name='add_resource'),
    path('resources/<int:pk>/edit/', views.edit_resource, name='edit_resource'),
    path('resources/<int:pk>/delete/', views.delete_resource, name='delete_resource'),
    path('marketplace/', views.marketplace, name='marketplace'),
    path('marketplace/add/', views.add_supply, name='add_supply'),
]
