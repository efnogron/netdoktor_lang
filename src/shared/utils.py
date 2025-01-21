from typing import List, Dict, Any
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
import os
from langchain_chroma import Chroma

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

def clear_vector_store(persist_dir: str, collection_name: str = "guidelines") -> None:
    """Clear the existing vector store."""
    try:
        import chromadb
        
        # Initialize ChromaDB client directly
        client = chromadb.PersistentClient(path=persist_dir)
        
        # Get current count
        print(f"\nClearing vector store...")
        
        try:
            # Delete the entire collection if it exists
            client.delete_collection(name=collection_name)
            print(f"Deleted collection: {collection_name}")
        except ValueError as e:
            print(f"Collection {collection_name} does not exist yet")
            
        # Create a new empty collection
        client.create_collection(name=collection_name)
        print("Created new empty collection")
        
        print("Vector store cleared successfully")
        
    except Exception as e:
        print(f"Error clearing vector store: {str(e)}")
        raise

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