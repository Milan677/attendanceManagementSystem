from django.db import models

# Create your models here.
class Admin(models.Model):
    name = models.CharField(max_length=255,unique=True,null=True,blank=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255,unique=True,blank=True)
    phone_number = models.CharField(max_length=10,null=True,blank=True)
    reset_token = models.CharField(max_length=64, null=True, blank=True)
    token_expiry = models.DateTimeField(null=True, blank=True)
    
    @property
    def is_authenticated(self):
        return True


