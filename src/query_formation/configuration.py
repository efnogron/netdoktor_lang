from dataclasses import dataclass, field
from typing import Annotated, Optional
from shared.configuration import BaseConfiguration

@dataclass
class QueryFormationConfig(BaseConfiguration):
    """Configuration for the query formation process."""
    
    # LLM settings
    llm_model: Annotated[str, {"kind": "llm"}] = field(
        default="gpt-4o-mini",
        metadata={"description": "LLM model for query formation"}
    )
    
    # Development settings
    max_sentences: Optional[int] = field(
        default=None,
        metadata={"description": "Maximum number of sentences to process (None for all)"}
    )
    
    # Processing settings
    min_claim_length: int = field(
        default=20,
        metadata={"description": "Minimum length for a verifiable claim"}
    )
    
    temperature: float = field(
        default=0.0,
        metadata={"description": "Temperature for LLM generation"}
    )
    
    max_tokens: int = field(
        default=2000,
        metadata={"description": "Maximum tokens for LLM response"}
    )
    
    # Output settings
    results_directory: str = field(
        default="results",
        metadata={"description": "Directory for storing verification results"}
    )
    
    # Logging settings
    log_directory: str = field(
        default="logs/query_formation",
        metadata={"description": "Directory for query formation logs"}
    ) 