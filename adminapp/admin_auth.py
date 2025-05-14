# admin_authentication.py
from rest_framework.authentication import BaseAuthentication
from rest_framework_simplejwt.tokens import AccessToken
from .models import Admin  
from rest_framework.exceptions import AuthenticationFailed

class AdminAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return None
        
        try:
            token_type, token = auth_header.split()
            if token_type.lower() != 'bearer':
                raise AuthenticationFailed('Invalid token header.')

            access_token = AccessToken(token)
            admin_id = access_token.get('user_id')  # or whatever field you saved
            if not admin_id:
                raise AuthenticationFailed('Invalid token payload.')

            admin = Admin.objects.get(id=admin_id)
            return (admin, None)  # First is user/admin, second is auth (None)

        except Exception as e:
            raise AuthenticationFailed('Invalid token: ' + str(e))
