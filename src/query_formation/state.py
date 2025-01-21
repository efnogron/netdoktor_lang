from dataclasses import dataclass, field
from typing import Dict, Optional, Any

@dataclass
class QueryContext:
    """Context information for query formation."""
    heading: str
    subheading: Optional[str]
    paragraph: str

@dataclass
class QueryFormationState:
    """State for the query formation process."""
    
    # Input state
    sentence: str
    context: QueryContext
    
    # Output state
    needs_verification: bool = False
    query: Optional[str] = None
    reasoning: Optional[str] = None
    
    # Processing state
    status: str = "initialized"
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert state to dictionary format."""
        return {
            "needs_verification": self.needs_verification,
            "query": self.query,
            "reasoning": self.reasoning
        } 