from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import redirect
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from .services.microsoft_oauth import MicrosoftOAuth
from rest_framework.permissions import AllowAny


class MicrosoftLoginView(APIView):
    permission_classes = [AllowAny] # acesso sem precisar de token

    def get(self, request):
        url = MicrosoftOAuth.get_authorization_url()
        return redirect(url)


class MicrosoftCallbackView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        code = request.GET.get("code")
        tokens = MicrosoftOAuth.exchange_code_for_token(code)
        id_token = tokens["id_token"]
        user_info = MicrosoftOAuth.decode_id_token(id_token)

        email = user_info.get("preferred_username")
        name = user_info.get("name")

        user, _ = User.objects.get_or_create(username=email, defaults={"email": email, "first_name": name})

        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        response = redirect("/api/chamados/")  # página da sua interface web
        response.set_cookie(
            key="jwt",
            value=access_token,
            httponly=True,   # não acessível via JS
            samesite="Lax",
            secure=False     # True em produção com HTTPS
        )
        return response