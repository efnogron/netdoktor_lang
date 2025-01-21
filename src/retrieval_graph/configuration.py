from dataclasses import dataclass, field
from typing import Annotated
from shared.configuration import BaseConfiguration

@dataclass
class RetrievalConfiguration(BaseConfiguration):
    """Configuration for the retrieval process."""
    
    # Search settings
    top_k: int = field(
        default=5,
        metadata={"description": "Number of top results to return"}
    )
    
    similarity_threshold: float = field(
        default=0.7,
        metadata={"description": "Minimum similarity score for results"}
    )
    
    # LLM settings
    llm_model: Annotated[str, {"kind": "llm"}] = field(
        default="gpt-4o-mini",
        metadata={"description": "LLM model for query processing"}
    ) 