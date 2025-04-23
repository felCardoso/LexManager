import requests
import json
from datetime import datetime
from config import DATAJUD_API_KEY


class DatajudAPI:
    def __init__(self):
        self.headers = {
            "Authorization": "ApiKey cDZHYzlZa0JadVREZDJCendQbXY6SkJlTzNjLV9TRENyQk1RdnFKZGRQdw==",
            "Content-Type": "application/json",
        }

        # Mapeamento de tribunais e suas URLs
        self.tribunais = {
            "TST": "https://api-publica.datajud.cnj.jus.br/api_publica_tst/_search",
            "TSE": "https://api-publica.datajud.cnj.jus.br/api_publica_tse/_search",
            "STJ": "https://api-publica.datajud.cnj.jus.br/api_publica_stj/_search",
            "STM": "https://api-publica.datajud.cnj.jus.br/api_publica_stm/_search",
            "TRF1": "https://api-publica.datajud.cnj.jus.br/api_publica_trf1/_search",
            "TRF2": "https://api-publica.datajud.cnj.jus.br/api_publica_trf2/_search",
            "TRF3": "https://api-publica.datajud.cnj.jus.br/api_publica_trf3/_search",
            "TRF4": "https://api-publica.datajud.cnj.jus.br/api_publica_trf4/_search",
            "TRF5": "https://api-publica.datajud.cnj.jus.br/api_publica_trf5/_search",
            "TRF6": "https://api-publica.datajud.cnj.jus.br/api_publica_trf6/_search",
            "TJAC": "https://api-publica.datajud.cnj.jus.br/api_publica_tjac/_search",
            "TJAL": "https://api-publica.datajud.cnj.jus.br/api_publica_tjal/_search",
            "TJAM": "https://api-publica.datajud.cnj.jus.br/api_publica_tjam/_search",
            "TJAP": "https://api-publica.datajud.cnj.jus.br/api_publica_tjap/_search",
            "TJBA": "https://api-publica.datajud.cnj.jus.br/api_publica_tjba/_search",
            "TJCE": "https://api-publica.datajud.cnj.jus.br/api_publica_tjce/_search",
            "TJDFT": "https://api-publica.datajud.cnj.jus.br/api_publica_tjdft/_search",
            "TJES": "https://api-publica.datajud.cnj.jus.br/api_publica_tjes/_search",
            "TJGO": "https://api-publica.datajud.cnj.jus.br/api_publica_tjgo/_search",
            "TJMA": "https://api-publica.datajud.cnj.jus.br/api_publica_tjma/_search",
            "TJMG": "https://api-publica.datajud.cnj.jus.br/api_publica_tjmg/_search",
            "TJMS": "https://api-publica.datajud.cnj.jus.br/api_publica_tjms/_search",
            "TJMT": "https://api-publica.datajud.cnj.jus.br/api_publica_tjmt/_search",
            "TJPA": "https://api-publica.datajud.cnj.jus.br/api_publica_tjpa/_search",
            "TJPB": "https://api-publica.datajud.cnj.jus.br/api_publica_tjpb/_search",
            "TJPE": "https://api-publica.datajud.cnj.jus.br/api_publica_tjpe/_search",
            "TJPI": "https://api-publica.datajud.cnj.jus.br/api_publica_tjpi/_search",
            "TJPR": "https://api-publica.datajud.cnj.jus.br/api_publica_tjpr/_search",
            "TJRJ": "https://api-publica.datajud.cnj.jus.br/api_publica_tjrj/_search",
            "TJRN": "https://api-publica.datajud.cnj.jus.br/api_publica_tjrn/_search",
            "TJRO": "https://api-publica.datajud.cnj.jus.br/api_publica_tjro/_search",
            "TJRR": "https://api-publica.datajud.cnj.jus.br/api_publica_tjrr/_search",
            "TJRS": "https://api-publica.datajud.cnj.jus.br/api_publica_tjrs/_search",
            "TJSC": "https://api-publica.datajud.cnj.jus.br/api_publica_tjsc/_search",
            "TJSE": "https://api-publica.datajud.cnj.jus.br/api_publica_tjse/_search",
            "TJSP": "https://api-publica.datajud.cnj.jus.br/api_publica_tjsp/_search",
            "TJTO": "https://api-publica.datajud.cnj.jus.br/api_publica_tjto/_search",
            "TRT1": "https://api-publica.datajud.cnj.jus.br/api_publica_trt1/_search",
            "TRT2": "https://api-publica.datajud.cnj.jus.br/api_publica_trt2/_search",
            "TRT3": "https://api-publica.datajud.cnj.jus.br/api_publica_trt3/_search",
            "TRT4": "https://api-publica.datajud.cnj.jus.br/api_publica_trt4/_search",
            "TRT5": "https://api-publica.datajud.cnj.jus.br/api_publica_trt5/_search",
            "TRT6": "https://api-publica.datajud.cnj.jus.br/api_publica_trt6/_search",
            "TRT7": "https://api-publica.datajud.cnj.jus.br/api_publica_trt7/_search",
            "TRT8": "https://api-publica.datajud.cnj.jus.br/api_publica_trt8/_search",
            "TRT9": "https://api-publica.datajud.cnj.jus.br/api_publica_trt9/_search",
            "TRT10": "https://api-publica.datajud.cnj.jus.br/api_publica_trt10/_search",
            "TRT11": "https://api-publica.datajud.cnj.jus.br/api_publica_trt11/_search",
            "TRT12": "https://api-publica.datajud.cnj.jus.br/api_publica_trt12/_search",
            "TRT13": "https://api-publica.datajud.cnj.jus.br/api_publica_trt13/_search",
            "TRT14": "https://api-publica.datajud.cnj.jus.br/api_publica_trt14/_search",
            "TRT15": "https://api-publica.datajud.cnj.jus.br/api_publica_trt15/_search",
            "TRT16": "https://api-publica.datajud.cnj.jus.br/api_publica_trt16/_search",
            "TRT17": "https://api-publica.datajud.cnj.jus.br/api_publica_trt17/_search",
            "TRT18": "https://api-publica.datajud.cnj.jus.br/api_publica_trt18/_search",
            "TRT19": "https://api-publica.datajud.cnj.jus.br/api_publica_trt19/_search",
            "TRT20": "https://api-publica.datajud.cnj.jus.br/api_publica_trt20/_search",
            "TRT21": "https://api-publica.datajud.cnj.jus.br/api_publica_trt21/_search",
            "TRT22": "https://api-publica.datajud.cnj.jus.br/api_publica_trt22/_search",
            "TRT23": "https://api-publica.datajud.cnj.jus.br/api_publica_trt23/_search",
            "TRT24": "https://api-publica.datajud.cnj.jus.br/api_publica_trt24/_search",
            "TRE-AC": "https://api-publica.datajud.cnj.jus.br/api_publica_tre-ac/_search",
            "TRE-AL": "https://api-publica.datajud.cnj.jus.br/api_publica_tre-al/_search",
            "TRE-AM": "https://api-publica.datajud.cnj.jus.br/api_publica_tre-am/_search",
            "TRE-AP": "https://api-publica.datajud.cnj.jus.br/api_publica_tre-ap/_search",
            "TRE-BA": "https://api-publica.datajud.cnj.jus.br/api_publica_tre-ba/_search",
            "TRE-CE": "https://api-publica.datajud.cnj.jus.br/api_publica_tre-ce/_search",
            "TRE-DFT": "https://api-publica.datajud.cnj.jus.br/api_publica_tre-dft/_search",
            "TRE-ES": "https://api-publica.datajud.cnj.jus.br/api_publica_tre-es/_search",
            "TRE-GO": "https://api-publica.datajud.cnj.jus.br/api_publica_tre-go/_search",
            "TRE-MA": "https://api-publica.datajud.cnj.jus.br/api_publica_tre-ma/_search",
            "TRE-MG": "https://api-publica.datajud.cnj.jus.br/api_publica_tre-mg/_search",
            "TRE-MS": "https://api-publica.datajud.cnj.jus.br/api_publica_tre-ms/_search",
            "TRE-MT": "https://api-publica.datajud.cnj.jus.br/api_publica_tre-mt/_search",
            "TRE-PA": "https://api-publica.datajud.cnj.jus.br/api_publica_tre-pa/_search",
            "TRE-PB": "https://api-publica.datajud.cnj.jus.br/api_publica_tre-pb/_search",
            "TRE-PE": "https://api-publica.datajud.cnj.jus.br/api_publica_tre-pe/_search",
            "TRE-PI": "https://api-publica.datajud.cnj.jus.br/api_publica_tre-pi/_search",
            "TRE-PR": "https://api-publica.datajud.cnj.jus.br/api_publica_tre-pr/_search",
            "TRE-RJ": "https://api-publica.datajud.cnj.jus.br/api_publica_tre-rj/_search",
            "TRE-RN": "https://api-publica.datajud.cnj.jus.br/api_publica_tre-rn/_search",
            "TRE-RO": "https://api-publica.datajud.cnj.jus.br/api_publica_tre-ro/_search",
            "TRE-RR": "https://api-publica.datajud.cnj.jus.br/api_publica_tre-rr/_search",
            "TRE-RS": "https://api-publica.datajud.cnj.jus.br/api_publica_tre-rs/_search",
            "TRE-SC": "https://api-publica.datajud.cnj.jus.br/api_publica_tre-sc/_search",
            "TRE-SE": "https://api-publica.datajud.cnj.jus.br/api_publica_tre-se/_search",
            "TRE-SP": "https://api-publica.datajud.cnj.jus.br/api_publica_tre-sp/_search",
            "TRE-TO": "https://api-publica.datajud.cnj.jus.br/api_publica_tre-to/_search",
            "TJMMG": "https://api-publica.datajud.cnj.jus.br/api_publica_tjmmg/_search",
            "TJMRS": "https://api-publica.datajud.cnj.jus.br/api_publica_tjmrs/_search",
            "TJMSP": "https://api-publica.datajud.cnj.jus.br/api_publica_tjmsp/_search",
        }

    def _identificar_tribunal(self, numero_processo):
        """Identifica o tribunal com base no número do processo"""
        # Remove caracteres não numéricos
        numero_limpo = "".join(filter(str.isdigit, numero_processo))

        # Verifica o dígito verificador (7º dígito)
        if len(numero_limpo) >= 7:
            digito = numero_limpo[6]

            # Mapeamento do dígito para o tribunal
            mapeamento = {
                "1": "TJSP",  # Justiça Estadual
                "2": "TRF1",  # Justiça Federal
                "3": "TRT1",  # Justiça do Trabalho
                "4": "TRE-SP",  # Justiça Eleitoral
                "5": "TJMSP",  # Justiça Militar
                "6": "STJ",  # Superior Tribunal de Justiça
                "7": "TST",  # Tribunal Superior do Trabalho
                "8": "TSE",  # Tribunal Superior Eleitoral
                "9": "STM",  # Superior Tribunal Militar
            }

            return mapeamento.get(digito, "TJSP")  # Retorna TJSP como padrão

        return "TJSP"  # Retorna TJSP como padrão se não conseguir identificar

    def buscar_processo(self, numero_processo):
        """Busca informações de um processo pelo número"""
        try:
            # Identifica o tribunal correto
            tribunal = self._identificar_tribunal(numero_processo)
            url = self.tribunais[tribunal]

            payload = json.dumps(
                {"query": {"match": {"numeroProcesso": numero_processo}}}
            )

            response = requests.request("POST", url, headers=self.headers, data=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Erro ao buscar processo: {e}")
            return None

    def buscar_movimentacoes(self, numero_processo):
        """Busca as movimentações de um processo"""
        try:
            tribunal = self._identificar_tribunal(numero_processo)
            url = self.tribunais[tribunal].replace("/_search", f"/processos/{numero_processo}/movimentacoes")
            
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Erro ao buscar movimentações: {e}")
            return None

    def buscar_documentos(self, numero_processo):
        """Busca os documentos de um processo"""
        try:
            tribunal = self._identificar_tribunal(numero_processo)
            url = self.tribunais[tribunal].replace("/_search", f"/processos/{numero_processo}/documentos")
            
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Erro ao buscar documentos: {e}")
            return None

    def sincronizar_processo(self, numero_processo):
        """Sincroniza as informações de um processo com o banco de dados local"""
        processo_data = self.buscar_processo(numero_processo)
        if not processo_data:
            return None

        # Atualiza ou cria o processo no banco de dados
        from db import Processo, db, Cliente
        from app import app
        from flask_login import current_user

        with app.app_context():
            # Obtém o primeiro cliente do advogado atual
            cliente = Cliente.query.filter_by(advogado_id=current_user.id).first()
            if not cliente:
                return None

            processo = Processo.query.filter_by(numero_processo=numero_processo).first()
            if not processo:
                processo = Processo(
                    numero_processo=numero_processo,
                    cliente_id=cliente.id,
                    advogado_id=current_user.id
                )

            # Atualiza os dados do processo
            processo.tribunal = processo_data.get("tribunal")
            processo.vara = processo_data.get("vara")
            processo.status = processo_data.get("status", "Ativo")
            processo.descricao = processo_data.get("descricao")
            processo.classe = processo_data.get("classe")
            processo.assunto = processo_data.get("assunto")
            processo.valor_causa = processo_data.get("valor_causa", 0.0)
            processo.ultima_atualizacao = datetime.utcnow()

            # Busca e atualiza as movimentações
            movimentacoes = self.buscar_movimentacoes(numero_processo)
            if movimentacoes:
                # Aqui você pode implementar a lógica para salvar as movimentações
                pass

            # Busca e atualiza os documentos
            documentos = self.buscar_documentos(numero_processo)
            if documentos:
                # Aqui você pode implementar a lógica para salvar os documentos
                pass

            db.session.add(processo)
            db.session.commit()

            return processo
