from django.db import models
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager,PermissionsMixin
from django.utils.timezone import now,timedelta
from django.utils.crypto import get_random_string

# Create your models here.
class CustomUserManager(BaseUserManager):
    def create_user(self,email,mobile_no,role,password=None,**extra_fields):
        if not email:
            raise ValueError("Email is required")
        if not mobile_no:
            raise ValueError("Mobile number is required")
        if not role:
            raise ValueError("role is required")
        
        email = self.normalize_email(email)
        user = self.model(email=email,mobile_no=mobile_no,role=role,**extra_fields)
        user.set_password(password)
        user.save(using = self._db)

        return user
    

class CustomUser(AbstractBaseUser,PermissionsMixin):
    ROLE_CHOICES = [
        ('student','Student'),
        ('teacher','Teacher'),
    ]

    email = models.EmailField(unique=True)
    mobile_no = models.CharField(max_length=15)
    role = models.CharField(max_length=10,choices=ROLE_CHOICES)
    registration_no = models.CharField(max_length=50,null=True,blank=True)
    faculty_id = models.CharField(max_length=50,null=True,blank=True)
    password = models.CharField(max_length=255)
    last_login = models.DateTimeField(default=now(),blank=True, null=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    reset_token = models.CharField(max_length=255, blank=True, null=True)
    reset_token_expiry = models.DateTimeField(blank=True, null=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['mobile_no']

    def save(self, *args, **kwargs):
        if self.role == 'student':
            self.faculty_id=None
            if not self.registration_no:
                raise ValueError("Registraion number is required for students")
        elif self.role == 'teacher':
            self.registration_no=None
            if not self.faculty_id:
                raise ValueError("Faculty ID is required for teachers")

        super().save(*args, **kwargs)

    def generate_reset_token(self):
        self.reset_token = get_random_string(50)
        self.reset_token_expiry = now() + timedelta(hours=1)
        self.save()            

    def __str__(self):
        return self.email    