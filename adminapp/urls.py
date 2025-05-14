from django.urls import path,include
from .views import *

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', loginAdmin, name='login-admin'),
    path('forgetPassword-admin/', forgetPassword, name='forget-password'),
    path('resetPassword-admin/<str:token>/', resetPassword, name='reset-password'),
    path('admin-logout/', logout_admin, name='logout-admin'),
    
]