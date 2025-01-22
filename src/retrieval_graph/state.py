from dataclasses import dataclass, field
from typing import Annotated, List, Optional
from langchain_core.documents import Document
from langgraph.graph.message import add_messages

@dataclass
class RetrievalState:
    """State management for the retrieval process."""
    
    query: str
    verification_reasoning: str
    messages: Annotated[List, add_messages] = field(default_factory=list)
    results: List[Document] = field(default_factory=list)
    status: Optional[str] = None 