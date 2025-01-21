from typing import Dict, Any, List
from pathlib import Path
from langchain_chroma import Chroma
from langgraph.graph import StateGraph, START, END

from .configuration import IndexConfiguration
from .state import IndexState
from shared.document_loader import load_and_split_pdf
from shared.utils import setup_embeddings

def find_pdf_files(directory: Path, recursive: bool = True) -> List[Path]:
    """Find all PDF files in the given directory."""
    pattern = "**/*.pdf" if recursive else "*.pdf"
    return list(directory.glob(pattern))

def create_index_graph(config: IndexConfiguration) -> StateGraph:
    """Create the indexing workflow graph."""
    
    # Initialize components
    embeddings = setup_embeddings(config.embedding_model)
    
    def load_documents(state: IndexState) -> Dict[str, Any]:
        """Load and process PDF documents."""
        all_chunks = []
        processed = []
        failed = []
        
        for file_path in state.input_files:
            try:
                chunks = load_and_split_pdf(
                    file_path,
                    chunk_size=config.chunk_size,
                    chunk_overlap=config.chunk_overlap
                )
                all_chunks.extend(chunks)
                processed.append(file_path)
            except Exception as e:
                failed.append(file_path)
                print(f"Failed to process {file_path}: {str(e)}")
        
        return {
            "documents": all_chunks,
            "processed_files": processed,
            "failed_files": failed,
            "status": "documents_loaded"
        }
    
    def index_documents(state: IndexState) -> Dict[str, Any]:
        """Index the processed documents."""
        try:
            vectorstore = Chroma(
                collection_name=config.collection_name,
                embedding_function=embeddings,
                persist_directory=str(config.persist_directory)
            )
            
            # Add documents to the vector store
            vectorstore.add_documents(state.documents)
            vectorstore.persist()
            
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