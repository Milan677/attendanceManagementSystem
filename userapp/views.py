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

