import json
import logging
from typing import Dict, Any
from pathlib import Path
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from datetime import datetime

from .configuration import QueryFormationConfig
from .state import QueryFormationState, QueryContext
from .prompts import QUERY_FORMATION_PROMPT

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
            tools=[{
                "type": "function",
                "function": {
                    "name": "format_analysis",
                    "description": "Format the analysis result as a JSON object",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "needs_verification": {
                                "type": "boolean",
                                "description": "Whether the sentence needs verification"
                            },
                            "query": {
                                "type": "string",
                                "description": "The verification query, starting with 'verify: ' or null if no verification needed"
                            },
                            "reasoning": {
                                "type": "string",
                                "description": "Explanation for the decision in German"
                            }
                        },
                        "required": ["needs_verification", "reasoning"]
                    }
                }
            }]
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
            
            # Access tool_calls from additional_kwargs
            if response.additional_kwargs.get('tool_calls'):
                tool_call = response.additional_kwargs['tool_calls'][0]
                # Get the arguments from the function call
                result = json.loads(tool_call['function']['arguments'])
                
                # Log the analysis
                self.logger.info(
                    f"Sentence: {sentence}\n"
                    f"Result: {result}\n"
                    f"Context: {context}\n"
                    f"---"
                )
                
                return result
            
            # If no tool calls, something went wrong
            self.logger.error(f"No tool calls in response: {response}")
            return {
                "needs_verification": False,
                "query": None,
                "reasoning": "Fehler bei der Analyse: Keine Tool-Antwort erhalten"
            }
            
        except Exception as e:
            self.logger.error(f"Error processing response: {str(e)}\nResponse: {response}")
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