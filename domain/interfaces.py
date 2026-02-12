from abc import ABC, abstractmethod
from typing import Callable, Dict, Any
from .entities import Alert

class AIAnalyzer(ABC):
    @abstractmethod
    def analyze_threat(self, alert_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyzes the alert/threat and returns enriched data."""
        pass

class AlertRepository(ABC):
    @abstractmethod
    def save_alert(self, alert: Alert) -> None:
        """Saves the alert to the persistence layer."""
        pass

class MessageConsumer(ABC):
    @abstractmethod
    def start_consuming(self, callback: Callable[[Dict[str, Any]], None]) -> None:
        """Starts consuming messages and calls the callback for each message."""
        pass
