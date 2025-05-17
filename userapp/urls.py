from django.urls import path, include
from .views import *

urlpatterns = [
    path('register/', userRegistrationView, name='user-register'),
    path('login/',userLoginView,name="user-login"),
    path('hii/',getUser),
    # teacher's schedule
    path('get-teacher-schedule/',teacherSchedule,name="teacher-schedules"),
    path('get-student-schedule/',studentSchedule,name="student-shedule"),
    path('create-qr/',createSessionAndQrCode,name='create-qr'),
    path('submit-attendance/',submitAttendance,name='submit-attendance'),
    path('get-attendance/<int:class_id>/',get_class_attendance_datewise,name="get-attendance"),
]