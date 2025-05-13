from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes,authentication_classes
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken,AccessToken
from django.contrib.auth.hashers import make_password,check_password
from .serializers import *
from .models import *

# Create your views here.

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([AllowAny])
def userRegistrationView(request):
    try:
        email = request.data.get('email')
        role = request.data.get('role')
        user = CustomUser.objects.filter(email=email,role=role).first()
        message=f"{role} with the given email already exist. Try with another email !"
        if user :
            return Response({"message":message})
        
        serializer = CustomUserSerializers(data = request.data)
        if serializer.is_valid():
            registraion_instance = serializer.save()
        return Response({'message': 'Registration successful'}, status=status.HTTP_201_CREATED)   
     
    except Exception as e:
        return Response({
            "error": str(e),
            "message": "Error occurred in registraion view"
        },status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([AllowAny])
def userLoginView(request):
    try:
        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            return Response({'error': 'Email and password are required'}, status=status.HTTP_400_BAD_REQUEST)
        
        user = CustomUser.objects.filter(email=email).first()
        if not user or not check_password(password,user.password):
            return Response({"error":"Invalid email or password !"},status=status.HTTP_401_UNAUTHORIZED)
        
        user.last_login = now()
        user.save(update_fields=['last_login'])

        refresh = RefreshToken.for_user(user)
        return Response({
                "message": "Login successful",
                "access_token": str(refresh.access_token),
                "refresh_token": str(refresh),    
            }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            "error": str(e),
            "message": "Error occurred in login view"
        },status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
def getUser(request):
    print("===========")
    print(request.user)
    return Response({"msg":"see terminal"})

