from django.utils import timezone
from chamados.models import Chamado, ItemChamado

class ChamadoService:

    @staticmethod
    def criar_chamado(dados, itens, usuario):
        chamado = Chamado.objects.create(
            solicitante=usuario,
            **dados
        )

        for item in itens:
            ItemChamado.objects.create(
                chamado=chamado,
                **item
            )
        return chamado

    @staticmethod
    def atualizar_status(chamado_id, novo_status):
        chamado = Chamado.objects.get(id=chamado_id)
        chamado.status = novo_status
        chamado.save()
        return chamado
