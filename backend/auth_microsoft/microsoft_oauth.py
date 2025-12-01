import requests
from jose import jwt
from django.conf import settings

class MicrosoftOAuth:

    @staticmethod
    def get_authorization_url():
        tenant = settings.MICROSOFT_TENANT_ID
        client_id = settings.MICROSOFT_CLIENT_ID
        redirect_uri = settings.MICROSOFT_REDIRECT_URI
        scope = settings.MICROSOFT_SCOPES

        return (
            f"https://login.microsoftonline.com/{tenant}/oauth2/v2.0/authorize"
            f"?client_id={client_id}"
            f"&response_type=code"
            f"&redirect_uri={redirect_uri}"
            f"&response_mode=query"
            f"&scope={scope.replace(' ', '%20')}"
        )

    @staticmethod
    def exchange_code_for_token(code):
        tenant = settings.MICROSOFT_TENANT_ID
        client_id = settings.MICROSOFT_CLIENT_ID
        client_secret = settings.MICROSOFT_CLIENT_SECRET
        redirect_uri = settings.MICROSOFT_REDIRECT_URI

        url = f"https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token"

        data = {
            "client_id": client_id,
            "client_secret": client_secret,
            "code": code,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code",
        }

        r = requests.post(url, data=data)
        r.raise_for_status()
        return r.json()

    @staticmethod
    def decode_id_token(id_token):
        tenant = settings.MICROSOFT_TENANT_ID
        jwks_url = f"https://login.microsoftonline.com/{tenant}/discovery/v2.0/keys"

        jwks = requests.get(jwks_url).json()
        headers = jwt.get_unverified_header(id_token)
        kid = headers["kid"]

        # Encontrar a chave correspondente dentro do JWKS
        key = next((k for k in jwks["keys"] if k["kid"] == kid), None)
        if not key:
            raise ValueError("Chave correspondente ao 'kid' do token não encontrada")

        return jwt.decode(
            id_token,
            key,
            algorithms=["RS256"],
            options={"verify_aud": False}
        )
