from dataclasses import dataclass, field
from typing import Annotated
from pathlib import Path

@dataclass
class BaseConfiguration:
    """Base configuration for the entire application."""
    
    # Document processing settings
    chunk_size: int = field(
        default=1000,
        metadata={"description": "Size of text chunks for splitting documents"}
    )
    chunk_overlap: int = field(
        default=100,
        metadata={"description": "Overlap between text chunks"}
    )
    
    # Model settings
    embedding_model: Annotated[str, {"kind": "embeddings"}] = field(
        default="text-embedding-3-small",
        metadata={"description": "OpenAI embedding model to use"}
    )
    
    # Path settings
    input_dir: Path = field(
        default=Path("input"),
        metadata={"description": "Directory containing input files"}
    )
    
    # Vector store settings
    vector_store_dir: Path = field(
        default=Path("vector_store"),
        metadata={"description": "Directory for storing vector databases"}
    ) 