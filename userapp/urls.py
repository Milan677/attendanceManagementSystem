from django.urls import path, include
from .views import *

urlpatterns = [
    path('register/', userRegistrationView, name='user-register'),
    path('login/',userLoginView,name="user-login"),
    path('hii/',getUser),
]