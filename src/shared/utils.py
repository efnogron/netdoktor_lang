from typing import List, Dict, Any
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
import os

def setup_embeddings(model_name: str = "text-embedding-3-small") -> OpenAIEmbeddings:
    """Initialize OpenAI embeddings.
    
    Args:
        model_name: Name of the OpenAI embedding model
        
    Returns:
        Configured OpenAI embeddings instance
    """
    return OpenAIEmbeddings(
        model=model_name,
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )

def format_results(documents: List[Document]) -> List[Dict[str, Any]]:
    """Format search results for display.
    
    Args:
        documents: List of retrieved documents
        
    Returns:
        List of formatted results with content and metadata
        
    Example:
        >>> results = format_results(retrieved_docs)
        >>> for r in results:
        >>>     print(f"Content: {r['content'][:100]}...")
    """
    return [
        {
            "content": doc.page_content,
            "metadata": doc.metadata,
            "score": doc.metadata.get("score", None)
        }
        for doc in documents
    ] 