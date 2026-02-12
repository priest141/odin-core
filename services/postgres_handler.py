import psycopg2
from psycopg2.extras import Json
from loguru import logger

from config import settings

class PostgresTacticalDB:
    def __init__(self):
        self.db_url = settings.DB_URL

        # DEBUG TÁTICO: Vamos ver o que o Odin está enxergando
        if self.db_url:
            # Mascara a senha para não vazar nos logs do Railway
            safe_url = re.sub(r':([^@]+)@', ':****@', self.db_url)
            logger.info(f"🔌 Tentando conectar em: {safe_url}")
        else:
            logger.error("❌ A variável DATABASE_URL está vazia ou None!")
            # Em produção no Railway, não devemos usar localhost como fallback.
            # É melhor falhar explicitamente para você saber que a config está errada.
            raise ValueError("DATABASE_URL is missing in Railway Environment")
            
        self.conn = None
        self._connect()
        self._init_schema()

    def _connect(self):
        try:
            self.conn = psycopg2.connect(self.db_url)
            self.conn.autocommit = True
            logger.info("🟢 Conectado ao PostgreSQL (CIV-INT DB).")
        except Exception as e:
            logger.error(f"🔴 Erro ao conectar no banco: {e}")

    def _init_schema(self):
        # Cria a tabela tática com suporte a JSONB para o briefing da IA
        query = """
        CREATE TABLE IF NOT EXISTS alertas_taticos (
            id SERIAL PRIMARY KEY,
            id_alerta BIGINT UNIQUE NOT NULL, -- ID original do IDAP para evitar duplicidade
            timestamp TIMESTAMPTZ NOT NULL,
            source VARCHAR(50),
            categoria VARCHAR(100),
            severidade VARCHAR(50),
            area_afetada VARCHAR(255),
            mensagem_tatica TEXT,
            briefing_ia JSONB, -- Onde a mágica da LLM fica armazenada
            data_processamento TIMESTAMPTZ DEFAULT NOW()
        );
        """
        try:
            with self.conn.cursor() as cur:
                cur.execute(query)
        except Exception as e:
            logger.error(f"Erro ao inicializar schema: {e}")

    def save_alert(self, enriched_alert):
        """Salva o alerta ou atualiza se já existir."""
        if not self.conn:
            self._connect()

        query = """
        INSERT INTO alertas_taticos (
            id_alerta, timestamp, source, categoria, 
            severidade, area_afetada, mensagem_tatica, briefing_ia
        ) VALUES (
            %(id_alerta)s, %(timestamp)s, %(source)s, %(categoria)s,
            %(severidade)s, %(area_afetada)s, %(mensagem_tática)s, %(briefing)s
        )
        ON CONFLICT (id_alerta) DO UPDATE SET
            severidade = EXCLUDED.severidade,
            mensagem_tatica = EXCLUDED.mensagem_tatica,
            briefing_ia = EXCLUDED.briefing_ia,
            data_processamento = NOW();
        """
        
        # O psycopg2.extras.Json cuida da conversão do dict Python para JSONB do Postgres
        data_to_insert = enriched_alert.copy()
        data_to_insert['briefing'] = Json(data_to_insert.get('briefing', {}))

        try:
            with self.conn.cursor() as cur:
                cur.execute(query, data_to_insert)
                logger.success(f"💾 Alerta {enriched_alert['id_alerta']} salvo/atualizado com sucesso no Postgres.")
        except Exception as e:
            logger.error(f"Falha ao inserir alerta no banco: {e}")

    def close(self):
        if self.conn:
            self.conn.close()
            logger.info("Conexão com o banco encerrada.")

# --- Integrando no Pipeline ---
if __name__ == "__main__":
    # Aquele alerta simulado que já passou pela sua classe TacticalAIAnalyzer
    alerta_processado = {
        "id_alerta": 173010,
        "timestamp": "2026-02-11T13:55:00",
        "source": "IDAP_DefesaCivil",
        "categoria": "Chuvas Intensas",
        "severidade": "Alta",
        "area_afetada": "Leme/SP",
        "mensagem_tática": "Chuva (20 a 40 mm), raios e ventos de 50 km/h.",
        "briefing": {
            "nivel_ameaca_tatico": "Alto",
            "impacto_infraestrutura": "Queda de energia e internet local.",
            "diretriz_acao": "1. Verificar lanternas. 2. Afastar de janelas. 3. Garantir reserva de água.",
            "necessidade_contato": True
        }
    }

    db = PostgresTacticalDB()
    db.save_alert(alerta_processado)
    db.close()