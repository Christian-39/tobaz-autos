"""
JWT Authentication for Tobaz Autos.
"""
import jwt
from datetime import datetime, timedelta
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import authentication, exceptions

User = get_user_model()


class JWTAuthentication(authentication.BaseAuthentication):
    """JWT Authentication class."""
    
    keyword = 'Bearer'
    
    def authenticate(self, request):
        auth_header = authentication.get_authorization_header(request).split()
        
        if not auth_header or auth_header[0].lower() != self.keyword.lower().encode():
            return None
        
        if len(auth_header) == 1:
            msg = 'Invalid token header. No credentials provided.'
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth_header) > 2:
            msg = 'Invalid token header. Token string should not contain spaces.'
            raise exceptions.AuthenticationFailed(msg)
        
        try:
            token = auth_header[1].decode('utf-8')
        except UnicodeError:
            msg = 'Invalid token header. Token string should not contain invalid characters.'
            raise exceptions.AuthenticationFailed(msg)
        
        return self.authenticate_credentials(token)
    
    def authenticate_credentials(self, token):
        """Validate JWT token."""
        try:
            payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed('Token has expired.')
        except jwt.InvalidTokenError:
            raise exceptions.AuthenticationFailed('Invalid token.')
        
        try:
            user = User.objects.get(id=payload['user_id'], is_active=True)
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed('User not found.')
        
        return (user, token)


def generate_jwt_token(user):
    """Generate JWT token for user."""
    payload = {
        'user_id': str(user.id),
        'username': user.username,
        'role': user.role,
        'exp': datetime.utcnow() + timedelta(seconds=settings.JWT_ACCESS_TOKEN_LIFETIME),
        'iat': datetime.utcnow(),
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm='HS256')


def decode_jwt_token(token):
    """Decode JWT token."""
    try:
        return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
