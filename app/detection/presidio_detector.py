import logging
from typing import List, Dict, Any
from presidio_analyzer import AnalyzerEngine, RecognizerResult
from presidio_analyzer.nlp_engine import NlpEngineProvider

logger = logging.getLogger(__name__)

class PresidioDetector:
    """Integrated Presidio Analyzer loaded with spaCy NLP engine."""

    def __init__(self, spacy_model: str = "en_core_web_lg", fallback_model: str = "en_core_web_sm"):
        self.analyzer = self._init_analyzer(spacy_model, fallback_model)

    def _init_analyzer(self, model_name: str, fallback: str) -> AnalyzerEngine:
        try:
            provider = NlpEngineProvider(
                nlp_configuration={
                    "nlp_engine_name": "spacy",
                    "models": [{"lang_code": "en", "model_name": model_name}],
                }
            )
            nlp_engine = provider.create_engine()
            logger.info(f"Loaded spaCy model '{model_name}' into Presidio Engine.")
            return AnalyzerEngine(nlp_engine=nlp_engine, supported_languages=["en"])
        except Exception as e:
            logger.warning(f"Could not load '{model_name}' ({e}). Trying fallback model '{fallback}'.")
            try:
                provider = NlpEngineProvider(
                    nlp_configuration={
                        "nlp_engine_name": "spacy",
                        "models": [{"lang_code": "en", "model_name": fallback}],
                    }
                )
                nlp_engine = provider.create_engine()
                logger.info(f"Loaded fallback spaCy model '{fallback}' into Presidio Engine.")
                return AnalyzerEngine(nlp_engine=nlp_engine, supported_languages=["en"])
            except Exception as e2:
                logger.error(f"Failed to load fallback spaCy model ({e2}). Initializing default AnalyzerEngine.")
                return AnalyzerEngine()

    def add_recognizer(self, recognizer: Any):
        """Adds custom recognizer to Presidio registry."""
        self.analyzer.registry.add_recognizer(recognizer)

    def analyze(self, text: str, entities: List[str] = None, score_threshold: float = 0.4) -> List[RecognizerResult]:
        """Analyzes text and returns detected PII entities."""
        if not text or not text.strip():
            return []
        try:
            return self.analyzer.analyze(
                text=text,
                language="en",
                entities=entities,
                score_threshold=score_threshold,
            )
        except Exception as e:
            logger.error(f"Presidio analyze error: {e}")
            return []
