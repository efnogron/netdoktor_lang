from dataclasses import dataclass, field
from pathlib import Path
from shared.configuration import BaseConfiguration

@dataclass
class IndexConfiguration(BaseConfiguration):
    """Configuration for the indexing process."""
    
    # Vector store settings
    collection_name: str = field(
        default="guidelines",
        metadata={"description": "Name of the vector store collection"}
    )
    
    persist_directory: Path = field(
        default=Path("vector_store"),
        metadata={"description": "Directory to persist the vector store"}
    )
    
    # Processing settings
    recursive_dir_search: bool = field(
        default=True,
        metadata={"description": "Whether to recursively search directories for PDFs"}
    )
    
    file_pattern: str = field(
        default="*.pdf",
        metadata={"description": "Pattern to match files for indexing"}
    ) 