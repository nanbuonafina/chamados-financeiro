from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .services.sankhya_service import SankhyaAPI


class EmpresasView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        empresas = SankhyaAPI.listar_empresas()
        return Response(empresas)

class ParceirosView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        parceiros = SankhyaAPI.listar_parceiros_fornecedores()
        return Response(parceiros)

class NaturezasView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        naturezas = SankhyaAPI.listar_naturezas()
        return Response(naturezas)
    
class CentrosResultadoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        centros_custo = SankhyaAPI.listar_centros_resultado()
        return Response(centros_custo)

class ProjetosView(APIView):
    def get(self, request):
        return Response(SankhyaAPI.listar_projetos())


class ProdutosView(APIView):
    def get(self, request):
        filtro = request.GET.get("descricao", "")
        codnat = request.GET.get("codnat", None)
        return Response(SankhyaAPI.listar_produtos(filtro, codnat))