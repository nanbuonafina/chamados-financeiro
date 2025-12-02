import os
import requests
from datetime import datetime
from django.core.cache import cache
from dotenv import load_dotenv

load_dotenv()

class SankhyaAPI:
    BASE_URL = os.getenv("SANKHYA_BASE_URL")
    TOKEN = os.getenv("SANKHYA_TOKEN")
    APPKEY = os.getenv("SANKHYA_APPKEY")
    USER = os.getenv("SANKHYA_USER")
    PASSWORD = os.getenv("SANKHYA_PASSWORD")

    SESSION_CACHE_KEY = "sankhya_bearer_token"
    SESSION_TIMEOUT = 60 * 30  # 30 minutos

    # =====================================================================
    # AUTENTICAÇÃO
    # =====================================================================
    @classmethod
    def authenticate(cls):
        """Autentica no Sankhya e salva o bearer token no cache."""
        url = f"{cls.BASE_URL}/login"
        headers = {
            "token": cls.TOKEN,
            "appkey": cls.APPKEY,
            "username": cls.USER,
            "password": cls.PASSWORD
        }

        response = requests.post(url, headers=headers)

        # debug do retorno sankhya
        #print("\n==== RESPOSTA DO LOGIN SANKHYA ====")
        #print("Status:", response.status_code)
        #print("Text:", response.text[:3000])
        #print("Headers:", headers)
        #print("URL:", url)
        #print("=================================\n")

        response.raise_for_status()
        data = response.json()

        token = data.get("bearerToken")
        if not token:
            raise RuntimeError("Token não encontrado na autenticação Sankhya")

        cache.set(cls.SESSION_CACHE_KEY, token, timeout=cls.SESSION_TIMEOUT)
        return token

    @classmethod
    def get_headers(cls):
        """Retorna headers com token válido."""
        token = cache.get(cls.SESSION_CACHE_KEY)
        if not token:
            token = cls.authenticate()

        return {
            "Authorization": f"Bearer {token}",
            "accept": "application/json",
            "Content-Type": "application/json",
            "appkey": cls.APPKEY
        }
    
    @staticmethod
    def map_generic_fields(entities, metadata):
        """
        Converte f0, f1, f2... para nomes reais dos campos.
        """
        field_map = {}
        fields_metadata = metadata.get("fields", {}).get("field", [])

        for i, meta in enumerate(fields_metadata):
            field_map[f"f{i}"] = meta.get("name")

        result = []
        for ent in entities:
            mapped = {}
            for fkey, fname in field_map.items():
                mapped[fname] = ent.get(fkey, {}).get("$")
            result.append(mapped)
        return result

    @classmethod
    def load_records(
        cls,
        root_entity: str,
        field_list: str,
        criteria: dict | None = None,
        limit: int = 500,
        paginated: bool = True
    ):
        page = 0
        all_records = []

        while True:
            body = {
                "requestBody": {
                    "dataSet": {
                        "rootEntity": root_entity,
                        "includePresentationFields": "N",
                        "offsetPage": str(page),
                        "limit": str(limit),
                        "entity": [
                            {
                                "path": "",
                                "fieldset": {
                                    "list": field_list
                                }
                            }
                        ]
                    }
                }
            }

            if criteria:
                body["requestBody"]["dataSet"]["criteria"] = criteria

            data = cls.call_service("CRUDServiceProvider.loadRecords", body)

            entities_data = data.get("responseBody", {}).get("entities", {})
            entities = entities_data.get("entity", [])
            metadata = entities_data.get("metadata", {})

            if isinstance(entities, dict):
                entities = [entities]

            if not entities:
                break

            mapped = cls.map_generic_fields(entities, metadata)
            all_records.extend(mapped)

            has_more = entities_data.get("hasMoreResult", "false") == "true"

            if not paginated or not has_more:
                break

            page += 1

        return all_records

    # =====================================================================
    # MÉTODO PADRÃO PARA CHAMAR QUALQUER SERVICE DO SANKHYA
    # =====================================================================
    @classmethod
    def call_service(cls, service_name: str, body: dict):
        """
        Método universal para chamadas CRUDServiceProvider.loadRecords
        ou qualquer outro service Sankhya.
        """

        url = f"{cls.BASE_URL}/gateway/v1/mge/service.sbr"
        headers = cls.get_headers()

        params = {
            "serviceName": service_name,
            "outputType": "json"
        }

        print("\n==== ENVIANDO REQUEST PARA SANKHYA ====")
        print("URL:", url)
        print("Params:", params)
        print("Headers:", headers)
        print("Body:", body)
        print("======================================\n")

        response = requests.post(url, headers=headers, params=params, json=body)

        print("\n==== RESPOSTA DO SERVICE ====")
        print("Status:", response.status_code)
        print("Text:", response.text[:4000])
        print("=================================\n")

        response.raise_for_status()

        try:
            return response.json()
        except Exception:
            raise RuntimeError("Sankhya não retornou JSON. Veja o log acima.")

    # =====================================================================
    # LISTAR EMPRESAS — AGORA CORRIGIDO COM call_service()
    # =====================================================================
    @classmethod
    def listar_empresas(cls):
        url = f"{cls.BASE_URL}/gateway/v1/mge/service.sbr"
        headers = cls.get_headers()

        params = {
            "serviceName": "CRUDServiceProvider.loadRecords",
            "outputType": "json"
        }

        payload = {
            "requestBody": {
                "dataSet": {
                    "rootEntity": "Empresa",
                    "includePresentationFields": "S",
                    "offsetPage": "0",
                    "entity": [
                        {
                            "path": "",
                            "fieldset": {"list": "CODEMP,NOMEFANTASIA"}
                        }
                    ]
                }
            }
        }

        print("\n==== ENVIANDO REQUEST PARA SANKHYA ====")
        print("URL:", url)
        print("Params:", params)
        print("Headers:", headers)
        print("Body:", payload)
        print("======================================\n")

        response = requests.post(url, headers=headers, params=params, json=payload)
        response.raise_for_status()

        print("\n==== RESPOSTA DO SERVICE ====")
        print("Status:", response.status_code)
        print("Text:", response.text)
        print("=================================\n")

        data = response.json()

        # Extrai registros
        entities = (
            data.get("responseBody", {})
                .get("entities", {})
                .get("entity", [])
        )

        # Se vier 1 item só, vira lista
        if isinstance(entities, dict):
            entities = [entities]

        empresas = []
        for e in entities:
            codigo = e.get("f0", {}).get("$")
            nome = e.get("f1", {}).get("$")
            empresas.append({"codigo": codigo, "nome": nome})

        return empresas

    # =====================================================================
    # ENVIAR NOTA — permanece igual
    # =====================================================================
    @classmethod
    def enviar_nota(cls, form_data: dict, lista_itens: list, debug=False):
        """
        Envia uma nota fiscal via CACSP.incluirNota.
        """

        url = f"{cls.BASE_URL}/gateway/v1/mgecom/service.sbr"
        headers = cls.get_headers()

        params = {
            "serviceName": "CACSP.incluirNota",
            "outputType": "json"
        }

        # Mapeia itens
        itens_payload = []
        for item in lista_itens:
            itens_payload.append({
                "NUNOTA": {},
                "CODPROD": {"$": item["codigo"]},
                "QTDNEG": {"$": str(item["quantidade"])},
                "CODVOL": {"$": item["codvol"]},
                "VLRUNIT": {"$": f"{item['vlrunit']:.2f}"},
                "PERCDESC": {"$": "0"},
                "AD_CODCENCUS": {"$": item["centro_resultado_codigo"]},
                "OBSERVACAO": {"$": item.get("observacao_item", "")},
            })

        cabecalho_payload = {
            "NUNOTA": {},
            "CODCENCUS": {"$": 1010109},
            "CODEMP": {"$": form_data["empresa_codigo"]},
            "CODPARC": {"$": form_data["parceiro_codigo"]},
            "DTNEG": {"$": form_data["data_emissao"]},
            "CODTIPOPER": {"$": form_data["tipo_operacao_codigo"]},
            "CODTIPVENDA": {"$": form_data["tipo_negociacao_codigo"]},
            "CODNAT": {"$": form_data["natureza_codigo"]},
            "CODPROJ": {"$": form_data["projeto_codigo"]},
            "OBSERVACAO": {"$": form_data.get("observacao", "")},
            "AD_OBSERVACAOINT": {"$": form_data.get("obs_interna", "")},
            "TIPMOV": {"$": "O"},
            "AD_INTEGRACAO": {"$": 1},
            "AD_FATLIB": {"$": "S"},
            "AD_DTLIB": {"$": datetime.now().strftime("%d/%m/%Y %H:%M:%S")},
        }

        payload = {
            "requestBody": {
                "nota": {
                    "cabecalho": cabecalho_payload,
                    "itens": {
                        "INFORMARPRECO": "True",
                        "item": itens_payload
                    }
                }
            }
        }

        response = requests.post(url, headers=headers, params=params, json=payload)

        if debug:
            print("\n=== DEBUG SANKHYA ===")
            print("STATUS:", response.status_code)
            print(response.text)
            print("=====================\n")

        response.raise_for_status()

        data = response.json()

        return data.get("responseBody", {}).get("chave", {}).get("NUNOTA", {}).get("$")
    
    @classmethod
    def listar_parceiros_fornecedores(cls):
        criteria = {
            "expression": {
                "$": "FORNECEDOR = ? AND ATIVO = ?"
            },
            "parameter": [
                {"$": "S", "type": "S"},
                {"$": "S", "type": "S"}
            ]
        }

        parceiros = cls.load_records(
            root_entity="Parceiro",
            field_list="CODPARC,NOMEPARC,CGC_CPF",
            criteria=criteria
        )

        resultado = []
        for p in parceiros:
            nome = p.get("NOMEPARC")
            cnpj = p.get("CGC_CPF")
            display = f"{nome} - {cnpj}" if cnpj else nome

            resultado.append({
                "codigo": p.get("CODPARC"),
                "nome": display
            })

        return resultado

    @classmethod
    def listar_entidades(cls, entidade_nome: str):
        entidades = {
            "Empresa": ("Empresa", "CODEMP,NOMEFANTASIA"),
            "Tipo Negociação": ("TipoNegociacao", "CODTIPVENDA,DESCRTIPVENDA"),
        }

        if entidade_nome not in entidades:
            raise ValueError(f"Entidade desconhecida: {entidade_nome}")

        root, campos = entidades[entidade_nome]

        rows = cls.load_records(root, campos)

        return [
            {"codigo": r.get(list(r.keys())[0]), "nome": r.get(list(r.keys())[1])}
            for r in rows
        ]


    @classmethod
    def listar_produtos(cls, filtro_desc: str = "", codnat: str = None):
        criteria_parts = ["ATIVO = 'S'"]

        if filtro_desc:
            criteria_parts.append(f"UPPER(DESCRPROD) LIKE UPPER('%{filtro_desc}%')")

        if codnat:
            try:
                codnat_int = int("".join(filter(str.isdigit, codnat)))
                criteria_parts.append(f"CODNAT = {codnat_int}")
            except ValueError:
                pass

        criteria = {
            "expression": {
                "$": " AND ".join(criteria_parts)
            }
        }

        produtos = cls.load_records(
            root_entity="Produto",
            field_list="CODPROD,DESCRPROD,COMPLDESC,CODVOL",
            criteria=criteria,
            limit=200
        )

        resultado = []
        for p in produtos:
            nome = p.get("COMPLDESC") or p.get("DESCRPROD")
            resultado.append({
                "codigo": p.get("CODPROD"),
                "nome": nome,
                "codvol": p.get("CODVOL"),
                "vlrunit": 0
            })

        return resultado
    
    @classmethod
    def listar_naturezas(cls):
        """
        Lista naturezas pela API v1 com filtros aplicados.
        """
        url_base = f"{cls.BASE_URL}/v1/naturezas"
        headers = cls.get_headers()

        CODIGOS_A_EXCLUIR = ("1", "2", "5", "6")
        filtros = {
            "tipoNatureza": 2,
            "analitica": True,
            "ativo": True
        }

        resultados = []
        page = 0

        while True:
            url = f"{url_base}?page={page}&modifiedSince=0"
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()

            data = response.json()

            registros = data.get("data", [])
            if not registros:
                break

            for r in registros:
                codigo = str(r.get("codigoNatureza", ""))

                # FILTROS
                if codigo.startswith(CODIGOS_A_EXCLUIR):
                    continue
                if r.get("tipoNatureza") != filtros["tipoNatureza"]:
                    continue
                if r.get("analitica") != filtros["analitica"]:
                    continue
                if r.get("ativo") != filtros["ativo"]:
                    continue

                resultados.append({
                    "codigo": codigo,
                    "nome": r.get("nome")
                })

            pagination = data.get("pagination", {})
            if pagination.get("hasMore", "false").lower() != "true":
                break

            page += 1

        return resultados
    
    @classmethod
    def listar_centros_resultado(cls):
        url_base = f"{cls.BASE_URL}/v1/centros-resultado"
        headers = cls.get_headers()

        resultados = []
        page = 0
        page_size = 50

        while True:
            url = f"{url_base}?page={page}&pageSize={page_size}"

            print("\n=== DEBUG – REQUEST CENTROS RESULTADO ===")
            print("URL:", url)
            print("Headers:", headers)

            response = requests.get(url, headers=headers, timeout=15)
            print("Status:", response.status_code)
            print("Response raw:", response.text[:4000])
            print("=========================================\n")

            response.raise_for_status()

            data = response.json()
            content = data.get("content") or data.get("data") or []

            if isinstance(content, dict):
                content = list(content.values())

            if not content:
                print("⚠️ Nenhum registro encontrado nesta página.")
                break

            for c in content:
                resultados.append({
                    "codigo": c.get("codigoCentroResultado"),
                    "nome": c.get("nome")
                })

            if len(content) < page_size:
                break

            page += 1

        return resultados
    
    @classmethod
    def listar_projetos(cls):
        url_base = f"{cls.BASE_URL}/v1/projetos"
        headers = cls.get_headers()

        resultados = []
        page = 0

        while True:
            url = f"{url_base}?page={page}"

            print("\n=== DEBUG – REQUEST PROJETOS ===")
            print("URL:", url)
            print("Headers:", headers)

            response = requests.get(url, headers=headers, timeout=15)
            print("Status:", response.status_code)
            print("Response raw:", response.text[:4000])
            print("==========================================\n")

            response.raise_for_status()

            data = response.json()

            # Detecta onde estão os dados
            content = (
                data.get("data")
                or data.get("content")
                or data.get("items")
                or data.get("records")
                or []
            )

            # Se vier como objeto com chave "data": [ ... ]
            if isinstance(content, dict):
                # tenta extrair automaticamente qualquer lista interna
                for val in content.values():
                    if isinstance(val, list):
                        content = val
                        break

            if not content:
                break

            for item in content:
                print("ITEM DEBUG:", item)  # <-- log para ver chaves reais

                # detecta automaticamente o campo do código
                codigo = (
                    item.get("codProj")
                    or item.get("codigo")
                    or item.get("codigoProjeto")
                    or item.get("id")
                    or item.get("codigoInterno")
                    or None
                )

                nome = (
                    item.get("descrProj")
                    or item.get("nome")
                    or item.get("descricao")
                    or "Sem Nome"
                )

                resultados.append({
                    "codigo": str(codigo),
                    "nome": nome
                })

            # fim da paginação
            if data.get("last") is True or data.get("pagination", {}).get("hasMore") == "false":
                break

            page += 1

        return resultados


