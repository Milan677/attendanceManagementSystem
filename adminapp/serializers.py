from rest_framework import serializers
from .models import *
from django.contrib.auth.hashers import make_password,check_password

class AdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Admin
        fields = '__all__'
        extra_kwargs = {
            'password':{'write_only':True}
        }  

    def create(self,validate_data):
        validate_data['password'] = make_password(validate_data['password'])
        return super().create(validate_data)      


