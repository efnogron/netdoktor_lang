from dataclasses import dataclass, field
from typing import List, Optional
from pathlib import Path
from langchain_core.documents import Document

@dataclass
class IndexState:
    """State for the indexing process."""
    
    input_files: List[Path]
    processed_files: List[Path] = field(default_factory=list)
    failed_files: List[Path] = field(default_factory=list)
    documents: List[Document] = field(default_factory=list)
    status: Optional[str] = None
    error_message: Optional[str] = None 