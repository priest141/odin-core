from domain.interfaces import AlertRepository
from domain.entities import Alert
from loguru import logger

try:
    from services.postgres_handler import PostgresTacticalDB
except ImportError:
    # Fallback for testing/verification without DB
    logger.warning("Could not import PostgresTacticalDB. Using stub.")
    class PostgresTacticalDB:
        def save_alert(self, data): pass

class PostgresAlertRepositoryAdapter(AlertRepository):
    def __init__(self):
        self.db = PostgresTacticalDB()

    def save_alert(self, alert: Alert) -> None:
        # The original code saved the enriched dict, so we extract it or mix it
        data_to_save = alert.enriched_data if alert.enriched_data else alert.raw_data
        # Ensure ID is there if needed
        if 'id_alerta' not in data_to_save:
             data_to_save['id_alerta'] = alert.id
        self.db.save_alert(data_to_save)
