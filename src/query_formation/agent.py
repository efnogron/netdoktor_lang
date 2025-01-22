import json
import logging
from typing import Dict, Any
from pathlib import Path
from langchain_openai import ChatOpenAI
from datetime import datetime

from .configuration import QueryFormationConfig
from .state import QueryContext
from .prompts import QUERY_FORMATION_PROMPT, QUERY_FORMATION_PROMPT_CONFIG

class QueryFormationAgent:
    """Agent for analyzing and forming verification queries from medical text."""
    
    def __init__(self, config: QueryFormationConfig):
        self.config = config
        base_model = ChatOpenAI(
            model=config.llm_model,
            temperature=config.temperature
        )
        
        # Bind the JSON formatting tool to the model
        self.llm = base_model.bind(
            tools=QUERY_FORMATION_PROMPT_CONFIG
        )
        
        # Setup logging
        log_dir = Path(config.log_directory)
        log_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger("query_formation")
        if not self.logger.handlers:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_handler = logging.FileHandler(
                log_dir / f"query_formation_{timestamp}.log",
                encoding='utf-8'
            )
            self.logger.addHandler(file_handler)
            self.logger.setLevel(logging.INFO)
        
        self.prompt = QUERY_FORMATION_PROMPT

    def analyze_sentence(self, sentence: str, context: QueryContext) -> Dict[str, Any]:
        """Analyze a sentence to determine if it needs verification."""
        
        if len(sentence.strip()) < self.config.min_claim_length:
            return {
                "needs_verification": False,
                "query": None,
                "reasoning": "Satz ist zu kurz für eine überprüfbare Aussage"
            }
        
        prompt_vars = {
            "heading": context.heading,
            "subheading": context.subheading,
            "paragraph": context.paragraph,
            "sentence": sentence
        }
        
        try:
            messages = self.prompt.format_messages(**prompt_vars)
            response = self.llm.invoke(messages)
            
            if response.additional_kwargs.get('tool_calls'):
                tool_call = response.additional_kwargs['tool_calls'][0]
                return json.loads(tool_call['function']['arguments'])
            
            return {
                "needs_verification": False,
                "query": None,
                "reasoning": "Fehler bei der Analyse: Keine Tool-Antwort erhalten"
            }
            
        except Exception as e:
            return {
                "needs_verification": False,
                "query": None,
                "reasoning": f"Fehler bei der Analyse: {str(e)}"
            }

    def process_text(self, text: str, context: QueryContext) -> Dict[str, Any]:
        """Process a complete text, analyzing each sentence."""
        sentences = text.split(". ")  # Simple sentence splitting
        results = []
        
        for sentence in sentences:
            if not sentence.strip():
                continue
                
            result = self.analyze_sentence(sentence, context)
            results.append({
                "sentence": sentence,
                "analysis": result
            })
        
        return {"results": results} 