from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import exceptions

class JWTFromCookieAuthentication(JWTAuthentication):

    def authenticate(self, request):
        # Pega o token do cookie
        token = request.COOKIES.get("jwt")

        if not token:
            return None  # Permite que o DRF continue procurando outras autenticações

        try:
            validated_token = self.get_validated_token(token)
            user = self.get_user(validated_token)
            return (user, validated_token)
        except exceptions.AuthenticationFailed:
            return None
