from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .services.sankhya_service import SankhyaAPI


class EmpresasView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        empresas = SankhyaAPI.listar_empresas()
        return Response(empresas)
