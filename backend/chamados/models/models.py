import uuid
from django.db import models
from django.contrib.auth.models import User


class Chamado(models.Model):
    STATUS_CHOICES = [
        ("Aberto", "Aberto"),
        ("Em análise", "Em análise"),
        ("Aprovado", "Aprovado"),
        ("Cancelado", "Cancelado"),
        ("Concluído", "Concluído"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    solicitante = models.ForeignKey(User, on_delete=models.PROTECT)

    # dados gerais do chamado
    empresa_codigo = models.CharField(max_length=20)
    parceiro_codigo = models.CharField(max_length=20)
    natureza_codigo = models.CharField(max_length=20)
    projeto_codigo = models.CharField(max_length=20)
    tipo_negociacao_codigo = models.CharField(max_length=20)
    tipo_operacao_codigo = models.CharField(max_length=20)
    moeda_codigo = models.CharField(max_length=10)

    obs_interna = models.TextField()

    empresa = models.CharField(max_length=255)
    parceiro = models.CharField(max_length=255)
    natureza = models.CharField(max_length=255)
    projeto = models.CharField(max_length=255)
    tipo_negociacao = models.CharField(max_length=255)

    data_emissao = models.DateField()

    pagamento_urgente = models.BooleanField(default=False)
    justificativa_urgencia = models.TextField(blank=True)

    produto_novo = models.BooleanField(default=False)
    nome_produto_novo = models.CharField(max_length=255, blank=True)

    parceiro_novo = models.BooleanField(default=False)
    nome_parceiro_novo = models.CharField(max_length=255, blank=True)
    cnpj_parceiro_novo = models.CharField(max_length=20, blank=True)

    pagamento_parcelado = models.BooleanField(default=False)
    descricao_parcelas = models.TextField(blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Aberto")

    data_criacao = models.DateTimeField(auto_now_add=True)
    data_alteracao = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Chamado {self.id} - {self.solicitante.username}"

# itens do chamado
class ItemChamado(models.Model):
    chamado = models.ForeignKey(Chamado, on_delete=models.CASCADE, related_name="itens")

    codigo = models.CharField(max_length=50)
    nome = models.CharField(max_length=255)
    codvol = models.CharField(max_length=10)
    quantidade = models.FloatField()
    vlrunit = models.DecimalField(max_digits=12, decimal_places=2)

    centro_resultado_codigo = models.CharField(max_length=20)
    produto_novo_flag = models.BooleanField(default=False)
    natureza_item_codigo = models.CharField(max_length=20)

    def __str__(self):
        return f"Item {self.codigo} do chamado {self.chamado.id}"

# anexo
class AnexoChamado(models.Model):
    chamado = models.OneToOneField(Chamado, on_delete=models.CASCADE, related_name="anexos")

    nota_fiscal = models.FileField(upload_to="notas_fiscais/", null=True, blank=True)
    boleto = models.FileField(upload_to="boletos/", null=True, blank=True)

    def __str__(self):
        return f"Anexos do chamado {self.chamado.id}"
