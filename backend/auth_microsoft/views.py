from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import redirect
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from .services.microsoft_oauth import MicrosoftOAuth


class MicrosoftLoginView(APIView):
    def get(self, request):
        url = MicrosoftOAuth.get_authorization_url()
        return redirect(url)


class MicrosoftCallbackView(APIView):
    def get(self, request):
        code = request.GET.get("code")

        tokens = MicrosoftOAuth.exchange_code_for_token(code)
        id_token = tokens["id_token"]

        user_info = MicrosoftOAuth.decode_id_token(id_token)

        email = user_info.get("preferred_username")
        name = user_info.get("name")

        user, created = User.objects.get_or_create(username=email, defaults={"email": email, "first_name": name})

        refresh = RefreshToken.for_user(user)

        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "email": email,
            "name": name
        })
