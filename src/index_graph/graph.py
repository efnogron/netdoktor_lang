from typing import Dict, Any, List
from pathlib import Path
from langchain_chroma import Chroma
from langgraph.graph import StateGraph, START, END

from .configuration import IndexConfiguration
from .state import IndexState
from shared.document_loader import load_and_split_pdf
from shared.utils import setup_embeddings
import chromadb
from chromadb.utils import embedding_functions
import os

def find_pdf_files(directory: Path, recursive: bool = True) -> List[Path]:
    """Find all PDF files in the given directory."""
    pattern = "**/*.pdf" if recursive else "*.pdf"
    return list(directory.glob(pattern))

def create_index_graph(config: IndexConfiguration) -> StateGraph:
    """Create the indexing workflow graph."""
    
    # Initialize components
    embeddings = setup_embeddings(config.embedding_model)
    
    # Use direct ChromaDB client
    client = chromadb.PersistentClient(path=str(config.persist_directory))
    collection = client.get_or_create_collection(
        name=config.collection_name,
        embedding_function=embedding_functions.OpenAIEmbeddingFunction(
            api_key=os.getenv("OPENAI_API_KEY"),
            model_name=config.embedding_model
        )
    )
    
    def load_documents(state: IndexState) -> Dict[str, Any]:
        """Load and process PDF documents."""
        all_chunks = []
        processed = []
        failed = []
        skipped = []
        
        # Get existing document sources
        existing_sources = {
            meta["source"] for meta in collection.get()["metadatas"]
        } if collection.count() > 0 else set()
        
        print(f"\nFound {len(existing_sources)} existing documents in vector store")
        
        for file_path in state.input_files:
            try:
                # Skip if already indexed
                if str(file_path) in existing_sources:
                    print(f"Skipping {file_path.name} - already indexed")
                    skipped.append(file_path)
                    continue
                    
                chunks = load_and_split_pdf(
                    file_path,
                    chunk_size=config.chunk_size,
                    chunk_overlap=config.chunk_overlap
                )
                all_chunks.extend(chunks)
                processed.append(file_path)
                print(f"Processed {file_path.name} - created {len(chunks)} chunks")
            except Exception as e:
                failed.append(file_path)
                print(f"Failed to process {file_path}: {str(e)}")
        
        return {
            "documents": all_chunks,
            "processed_files": processed,
            "failed_files": failed,
            "skipped_files": skipped,
            "status": "documents_loaded"
        }
    
    def index_documents(state: IndexState) -> Dict[str, Any]:
        """Index the processed documents."""
        try:
            if not state.documents:
                print("No new documents to index")
                return {"status": "no_new_documents"}
                
            # Convert documents to ChromaDB format
            documents = []
            embeddings = []
            metadatas = []
            ids = []
            
            for i, doc in enumerate(state.documents):
                documents.append(doc.page_content)
                metadatas.append(doc.metadata)
                ids.append(f"doc_{i}")
            
            # Add documents using ChromaDB native interface
            collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            
            print(f"Successfully indexed {len(state.documents)} new chunks")
            print(f"Total collection size: {collection.count()}")
            
            return {"status": "indexing_completed"}
        except Exception as e:
            return {
                "status": "indexing_failed",
                "error_message": str(e)
            }
    
    # Create and compile graph
    workflow = StateGraph(IndexState)
    
    # Add nodes
    workflow.add_node("load_documents", load_documents)
    workflow.add_node("index_documents", index_documents)
    
    # Add edges
    workflow.add_edge(START, "load_documents")
    workflow.add_edge("load_documents", "index_documents")
    workflow.add_edge("index_documents", END)
    
    return workflow.compile()

# Create the default graph instance
graph = create_index_graph(IndexConfiguration()) 