from dataclasses import dataclass, field
from typing import Annotated
from shared.configuration import BaseConfiguration
from pathlib import Path

@dataclass
class RetrievalConfiguration:
    """Configuration for retrieval workflow."""
    
    # Model settings
    embedding_model: str = "text-embedding-3-small"
    llm_model: str = "gpt-4o-mini"
    
    # Vector store settings
    collection_name: str = "guidelines"  # Updated to match index configuration
    vector_store_dir: Path = Path("vector_store")
    
    # Search settings
    top_k: int = 5
    
    similarity_threshold: float = field(
        default=0.7,
        metadata={"description": "Minimum similarity score for results"}
    )
