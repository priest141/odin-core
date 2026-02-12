from typing import Dict, Any
from domain.interfaces import AIAnalyzer
from loguru import logger

try:
    from services.gemini_handler import TacticalAIAnalyzer
except ImportError:
    logger.warning("Could not import TacticalAIAnalyzer. Using stub.")
    class TacticalAIAnalyzer:
        def __init__(self): pass
        def analyze_threat(self, data): return {"threat_level": "unknown", "briefing": "Stubbed analysis"}

class GeminiAnalyzerAdapter(AIAnalyzer):
    def __init__(self):
        self.analyzer = TacticalAIAnalyzer()

    def analyze_threat(self, alert_data: Dict[str, Any]) -> Dict[str, Any]:
        return self.analyzer.analyze_threat(alert_data)
