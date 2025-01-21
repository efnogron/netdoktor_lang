from dataclasses import dataclass, field
from pathlib import Path
from shared.configuration import BaseConfiguration

@dataclass
class IndexConfiguration(BaseConfiguration):
    """Configuration for document indexing."""
    
    # Document processing settings
    chunk_size: int = 1000
    chunk_overlap: int = 100
    
    # Model settings
    embedding_model: str = "text-embedding-3-small"
    
    # Vector store settings
    collection_name: str = "guidelines"  # Use same name
    persist_directory: Path = Path("vector_store")
    
    # Processing settings
    recursive_dir_search: bool = field(
        default=True,
        metadata={"description": "Whether to recursively search directories for PDFs"}
    )
    
    file_pattern: str = field(
        default="*.pdf",
        metadata={"description": "Pattern to match files for indexing"}
    ) 