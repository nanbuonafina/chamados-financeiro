from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from ..models.models import Chamado
from ..serializers.serializers import ChamadoSerializer
from ...sankhya.services.sankhya_service import SankhyaAPI


class ChamadoViewSet(viewsets.ModelViewSet):
    queryset = Chamado.objects.all()
    serializer_class = ChamadoSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        """
        Chamado automaticamente vinculado ao usuário logado.
        Após salvar, integra com a API do Sankhya.
        """
        chamado = serializer.save(solicitante=self.request.user)

        # Prepara dados para o Sankhya
        form_data = {
            "empresa_codigo": chamado.empresa_codigo,
            "parceiro_codigo": chamado.parceiro_codigo,
            "natureza_codigo": chamado.natureza_codigo,
            "projeto_codigo": chamado.projeto_codigo,
            "tipo_negociacao_codigo": chamado.tipo_negociacao_codigo,
            "tipo_operacao_codigo": chamado.tipo_operacao_codigo,
            "moeda_codigo": chamado.moeda_codigo,
            "obs_interna": chamado.obs_interna,
            "data_emissao": chamado.data_emissao.strftime("%d/%m/%Y"),
        }

        itens = list(chamado.itens.all().values(
            "codigo",
            "nome",
            "codvol",
            "quantidade",
            "vlrunit",
            "centro_resultado_codigo",
            "produto_novo_flag",
            "natureza_item_codigo",
        ))

        # Chama o Sankhya
        try:
            nunota = SankhyaAPI.enviar_nota(form_data, itens)
            print("Nota enviada com sucesso:", nunota)
        except Exception as e:
            print("Erro ao enviar nota:", e)

        return chamado
