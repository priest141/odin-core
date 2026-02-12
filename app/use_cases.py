from typing import Dict, Any
from loguru import logger
from domain.entities import Alert
from domain.interfaces import AIAnalyzer, AlertRepository

class ProcessAlertUseCase:
    def __init__(self, analyzer: AIAnalyzer, repository: AlertRepository):
        self.analyzer = analyzer
        self.repository = repository

    def execute(self, raw_alert_data: Dict[str, Any]):
        alert_id = raw_alert_data.get('id_alerta', 'unknown')
        logger.info(f"Processing alert {alert_id}...")
        
        # 1. Analyze (enrich)
        enriched_data = self.analyzer.analyze_threat(raw_alert_data)
        
        # 2. Create Entity
        alert = Alert(id=alert_id, raw_data=raw_alert_data, enriched_data=enriched_data)
        
        # 3. Save
        self.repository.save_alert(alert)
        logger.info(f"Alert {alert_id} processed and saved.")
        
