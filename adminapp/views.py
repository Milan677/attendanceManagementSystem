from django.shortcuts import render

# Create your views here.
from rest_framework.decorators import api_view, permission_classes,authentication_classes
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets
from .admin_auth import AdminAuthentication
from rest_framework_simplejwt.tokens import RefreshToken,AccessToken
from django.contrib.auth.hashers import make_password,check_password
from .serializers import *
import datetime
from django.utils.crypto import get_random_string
from django.conf import settings
from django.core.mail import send_mail
from userapp.models import *
from userapp.serializers import *



@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    try:
        serializer = AdminSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "New admin registered successfully!"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            "error": str(e),
            "message": "Error occurred in register view"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# login view..............       

@api_view(['POST'])
@permission_classes([AllowAny])
def loginAdmin(request):
    try:
        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            return Response({'error': 'Email and password are required'}, status=status.HTTP_400_BAD_REQUEST)

        admin = Admin.objects.filter(email=email).first()

        if admin and check_password(password, admin.password):
            access = AccessToken()
            access['user_id'] = admin.id
            access['email'] = admin.email
            access['admin_name'] = admin.name
            access.set_exp(lifetime=datetime.timedelta(minutes=60))  # 30 min expiry

            # Create Refresh Token manually
            refresh = RefreshToken()
            refresh['user_id'] = admin.id
            refresh['email'] = admin.email
            refresh['admin_name'] = admin.name
            refresh.set_exp(lifetime=datetime.timedelta(days=7))  # 7 day expiry

            # Send response
            return Response(
                  {
                    "message": "Login successful.",
                    "admin": {
                        "id": admin.id,
                        "name": admin.name,
                        "email": admin.email,
                    },
                   "access_token": str(access),
                   "refresh_token": str(refresh),
                 },
                 status=status.HTTP_200_OK,
            )
        
        return Response({"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)
    
    except Exception as e:
        return Response({
            "error": str(e),
            "message": "Error occurred in login view"
        },status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# forget password.......
@api_view(['POST'])
@authentication_classes([AdminAuthentication])
@permission_classes([AllowAny])
def forgetPassword(request):
    try:
        email = request.data.get('email')
        if not email:
            return Response({"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        admin = Admin.objects.filter(email=email).first()
        if not admin:
            return Response({"error": "Email not found"}, status=status.HTTP_404_NOT_FOUND)

        # Generate a reset token
        reset_token = get_random_string(length=64)
        Admin.objects.filter(email=email).update(reset_token=reset_token)


        # Send the password reset link to the user's email
        reset_link=f"{settings.FRONTEND_URL}admin_reset_password/{reset_token}"
        send_mail(
            "Password Reset Request",
            f"Click the link to reset your password: {reset_link}",
            settings.DEFAULT_FROM_EMAIL,
            [admin.email]
        )

        return Response({
            "message": "Password reset link sent to your email.",
            "reset_token": reset_token},
            status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            "error": str(e),
            "message": "Error occurred in login view"
        },status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# reset password
@api_view(['POST'])
@permission_classes([AllowAny])
def resetPassword(request,token):
    try:        
        new_password = request.data.get('new_password')
        if not new_password:
            return Response({"error": "New password is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        user = Admin.objects.filter(reset_token=token).first()
        if not user:
            return Response({"error": "Invalid or expired token"}, status=status.HTTP_400_BAD_REQUEST)

        # Update the password
        new_password = make_password(new_password)
        Admin.objects.filter(reset_token=token).update(password=new_password,reset_token=None)
        
        return Response({"message": "Password reset successful."}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            "error": str(e),
            "message": "Error occurred in login view"
        },status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# logout admin
@api_view(['POST'])
@authentication_classes([AdminAuthentication])
@permission_classes([IsAuthenticated])
def logout_admin(request):
    try:
       refresh_token = request.data.get('refresh')
       if not refresh_token:
           return Response({"error":"Refresh token is required."},status=status.HTTP_400_BAD_REQUEST)
       
       token = RefreshToken(refresh_token)
       token.blacklist()

       return Response({"message":"Logout successful."},status=status.HTTP_205_RESET_CONTENT)
     
    except Exception as e:
        return Response({
            "error": str(e),
            "message": "Error occurred in logout admin view"
        },status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@authentication_classes([AdminAuthentication])
@permission_classes([IsAuthenticated])
def create_class(request):
    try:
        serializer = ClassSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            "error":str(e),
            "message":"Error occured in create_class admin view"
        },status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    


@api_view(['POST'])
@authentication_classes([AdminAuthentication])
@permission_classes([IsAuthenticated])
def shedule_classes(request):
    try:
        serializer = ClassScheduleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            "error":str(e),
            "message":"Error occured in shedule_classes admin view"
        },status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

    