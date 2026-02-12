import json
import google.generativeai as genai
from loguru import logger
from google.ai.generativelanguage_v1beta.types import content

from config import settings

class TacticalAIAnalyzer:
    def __init__(self):
        # Pega a chave do ambiente via Config
        api_key = settings.GEMINI_API_KEY
        if not api_key:
            logger.error("❌ GEMINI_API_KEY not found in settings!")
            raise ValueError("API Key is missing")

        genai.configure(api_key=api_key)

        # Configuração para garantir resposta em JSON limpo
        self.generation_config = {
            "temperature": 0.2, # Baixa criatividade, alto determinismo tático
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 1024,
            "response_mime_type": "application/json",
        }

        # O System Prompt agora entra na inicialização do modelo
        self.system_instruction = """
        Você é o ODIN, o núcleo de inteligência (CIV-INT) de um dashboard de sobrevivencialismo.
        Sua função é analisar alertas da Defesa Civil e gerar diretrizes táticas imediatas.
        
        PERFIL OPERACIONAL:
        1. Mentalidade: Sobrevivencialismo, Bushcraft, Militar.
        2. Foco: Proteção da família e integridade da infraestrutura (energia, água, rotas).
        3. Estilo: Curto, direto, sem alarmismo desnecessário, mas brutalmente honesto sobre riscos.
        
        SAÍDA OBRIGATÓRIA (JSON):
        Você DEVE retornar um JSON com esta estrutura exata:
        {
            "nivel_ameaca_tatico": "Baixo | Médio | Alto | Crítico",
            "impacto_estimado": "Resumo de 1 frase sobre o que vai falhar (ex: Queda de árvores na via principal, corte de luz)",
            "plano_acao": [
                "Ação 1 (Imediata)",
                "Ação 2 (Preparação)",
                "Ação 3 (Monitoramento)"
            ],
            "acionar_contato_familia": true/false
        }
        """

        # Usando o modelo Flash por ser mais rápido e eficiente para tarefas repetitivas
        self.model = genai.GenerativeModel(
            model_name=settings.GEMINI_MODEL, 
            generation_config=self.generation_config,
            system_instruction=self.system_instruction
        )

        # Contexto do Perímetro (Hardcoded ou vindo de config)
        self.perimeter_context = {
            "RIO CLARO": "Base Principal (Jd. Portugal). Operador e Esposa.",
            "LEME": "Base Secundária (Crítica). Filho (Gael) e Pais.",
            "SÃO PAULO": "Base Terciária. Irmã.",
            "CORDEIRÓPOLIS": "Rota de fuga/trânsito.",
            "ARARAS": "Rota de fuga/trânsito."
        }

    def _get_tactical_context(self, text_location):
        # Busca simples de string para injetar contexto
        loc_upper = text_location.upper()
        contextos = [desc for cidade, desc in self.perimeter_context.items() if cidade in loc_upper]
        
        if contextos:
            return " | ".join(contextos)
        return "Zona externa ao perímetro primário. Monitorar por efeito cascata."

    def analyze_threat(self, alert_data):
        try:
            # Extrai dados do alerta bruto
            severidade = alert_data.get('severidade', 'Desconhecida')
            categoria = alert_data.get('categoria', 'Evento Geral')
            msg = alert_data.get('mensagem_tática', '') or alert_data.get('descricao', '')
            local = alert_data.get('area_afetada', 'Desconhecido')

            logger.info(f"⚡ Gemini processando alerta: {categoria} em {local}")

            # Monta o prompt do usuário com os dados dinâmicos
            contexto_local = self._get_tactical_context(local)
            
            user_prompt = f"""
            DADOS DE INTELIGÊNCIA (SIGINT/OSINT):
            - Evento: {categoria}
            - Severidade Oficial: {severidade}
            - Local: {local}
            - Mensagem Interceptada: "{msg}"
            
            CONTEXTO DO OPERADOR:
            {contexto_local}
            
            Analise e gere o JSON tático.
            """

            # Gera a resposta
            response = self.model.generate_content(user_prompt)
            
            # Parsing do JSON nativo do Gemini
            tactical_briefing = json.loads(response.text)
            
            # Retorna o alerta original enriquecido com a inteligência do Odin
            return {**alert_data, "briefing": tactical_briefing}

        except Exception as e:
            logger.error(f"⚠️ Falha na análise tática do Gemini: {e}")
            # Fallback seguro para não quebrar o pipeline
            return {
                **alert_data, 
                "briefing": {
                    "nivel_ameaca_tatico": "Erro de Análise",
                    "impacto_estimado": "Falha no processamento neural.",
                    "plano_acao": ["Verificar logs do Odin", "Monitorar manualmente"],
                    "acionar_contato_familia": True
                }
            }

# --- Teste de Bancada (Executar diretamente este arquivo) ---
if __name__ == "__main__":
    # Simula um alerta vindo do Redis
    mock_alert = {
        "id_alerta": 999,
        "categoria": "Tempestade de Raios",
        "severidade": "Muito Alta",
        "area_afetada": "LEME/SP",
        "mensagem_tática": "Defesa Civil: Chuva severa nas próximas 2h. Ventos > 80km/h."
    }

    try:
        brain = TacticalAIAnalyzer()
        resultado = brain.analyze_threat(mock_alert)
        print(json.dumps(resultado, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"Erro no teste: {e}")