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
import uuid
from django.utils import timezone
import qrcode
from io import BytesIO

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
                "user":{
                    "email":user.email,
                    "role":user.role,
                },
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

# teacher's shedule
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
def teacherSchedule(request):
    try:
        teacher = request.user
        shedules = ClassSchedule.objects.filter(teacher = teacher)
        if not shedules:
            return Response({"message":"No shedule for the teacher ID"})
        
        serializer = ClassScheduleSerializer(shedules,many=True)
        return Response({"data":serializer.data},status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            "error": str(e),
            "message": "Error occurred in login view"
        },status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
def studentSchedule(request):
    try:
        user = request.user

        if user.role != 'student':
            return Response({"detail": "Only students can access this endpoint."}, status=403)

        # Get all schedules for classes the student is enrolled in
        schedules = ClassSchedule.objects.filter(classroom__students=user).select_related('classroom', 'teacher')

        serializer = ClassScheduleSerializer(schedules, many=True)
        return Response(serializer.data)
    except Exception as e:
        return Response({
            "error": str(e),
            "message": "Error occurred in login view"
        },status=status.HTTP_500_INTERNAL_SERVER_ERROR)

import base64

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
def createSessionAndQrCode(request):
    try:
        teacher = request.user
        schedule_id = request.data.get('schedule_id')
        schedule = ClassSchedule.objects.get(id=schedule_id, teacher=teacher)
        if not schedule:
            return Response({"error":"invalid shedule"})
        
        session_code = uuid.uuid4().hex
        expires_at = timezone.now() + timezone.timedelta(minutes=30)

        session = AttendanceSession.objects.create(
            schedule=schedule,
            session_code=session_code,
            expires_at=expires_at
        )

        qr = qrcode.make(session.session_code)
        buffer = BytesIO()
        qr.save(buffer, format="PNG")
        buffer.seek(0)

        img_base64 = base64.b64encode(buffer.read()).decode('utf-8')

        return Response({
            "session_code": session.session_code,
            "expires_at": session.expires_at,
            "qr_code": img_base64  
        })

    except Exception as e:
        return Response({
            "error": str(e),
            "message": "Error occurred in user app"
        },status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
def submitAttendance(request):
    try:
        student = request.user
        session_code = request.data.get('session_code')
        session = AttendanceSession.objects.get(session_code=session_code)
        if not session:
            return Response({"error":"Invalid session code !"})
        
        if not session.is_active():
            return Response({"error": "Session expired"}, status=400)
        
        classroom = session.schedule.classroom
        if not classroom.students.filter(id=student.id).exists():
            return Response({"error": "You are not enrolled in this class"}, status=403)
        
        attendance, created = Attendance.objects.get_or_create(
            student=student,
            session=session,
            defaults={'classroom': classroom}
        )

        if not created:
            return Response({"message": "Attendance already marked"})

        return Response({"message": "Attendance submitted successfully"})
    
    except Exception as e:
        return Response({
            "error": str(e),
            "message": "Error occurred in user app"
        },status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    