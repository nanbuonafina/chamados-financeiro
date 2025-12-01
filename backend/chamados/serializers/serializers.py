from rest_framework import serializers
from ..models.models import Chamado, ItemChamado, AnexoChamado


class ItemChamadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemChamado
        fields = "__all__"


class AnexoChamadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnexoChamado
        fields = "__all__"


class ChamadoSerializer(serializers.ModelSerializer):
    itens = ItemChamadoSerializer(many=True, required=False)
    anexos = AnexoChamadoSerializer(required=False)

    class Meta:
        model = Chamado
        fields = "__all__"
        read_only_fields = ["solicitante", "data_criacao", "data_alteracao"]

    def create(self, validated_data):
        itens_data = validated_data.pop("itens", [])
        anexos_data = validated_data.pop("anexos", None)

        # Solicitante = usuário autenticado
        user = self.context["request"].user
        chamado = Chamado.objects.create(solicitante=user, **validated_data)

        # Cria itens
        for item in itens_data:
            ItemChamado.objects.create(chamado=chamado, **item)

        # Cria anexos (one-to-one)
        if anexos_data:
            AnexoChamado.objects.create(chamado=chamado, **anexos_data)

        return chamado
