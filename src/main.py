import os
from pathlib import Path
from dotenv import load_dotenv

from index_graph.configuration import IndexConfiguration
from index_graph.state import IndexState
from index_graph.graph import graph as index_graph

from retrieval_graph.configuration import RetrievalConfiguration
from retrieval_graph.state import RetrievalState
from retrieval_graph.graph import graph as retrieval_graph

# Load environment variables
load_dotenv()

def index_guidelines():
    """Index the medical guidelines."""
    print("Starting indexing process...")
    
    # Get the absolute path to the project root
    project_root = Path(__file__).parent.parent
    
    # Configure indexing
    config = IndexConfiguration(
        collection_name="asthma_guidelines",
        persist_directory=project_root / "vector_store",
        chunk_size=1000,
        chunk_overlap=100
    )
    
    # Initialize state with input file using absolute path
    guideline_path = project_root / "input/asthma/guideline/guideline.pdf"  # Updated path
    
    # Verify file exists
    if not guideline_path.exists():
        raise FileNotFoundError(f"Guideline file not found at: {guideline_path}")
        
    print(f"Processing guideline file: {guideline_path}")
    initial_state = IndexState(input_files=[guideline_path])
    
    # Run indexing
    try:
        result = index_graph.invoke(initial_state)
        print(f"\nIndexing completed!")
        print(f"Processed files: {len(result['processed_files'])}")
        if result['failed_files']:
            print(f"Failed files: {len(result['failed_files'])}")
    except Exception as e:
        print(f"Indexing failed: {str(e)}")

def search_guidelines(query: str):
    """Search the indexed guidelines."""
    print(f"\nSearching for: {query}")
    
    # Configure retrieval
    config = RetrievalConfiguration(
        top_k=3,
        similarity_threshold=0.7
    )
    
    # Initialize state with query
    initial_state = RetrievalState(query=query)
    
    # Run search
    try:
        result = retrieval_graph.invoke(initial_state)
        print("\nSearch Results:")
        for message in result['messages']:
            print(f"\n{message.content}")
    except Exception as e:
        print(f"Search failed: {str(e)}")

def main():
    """Main execution function."""
    # First, index the guidelines
    index_guidelines()
    
    # Then test with a sample query
    test_query = "verify this statement: If the trigger for allergic asthma is a pollen or house dust mite allergy, allergen-specific immunotherapy (AIT or hyposensitisation) is recommended."
    search_guidelines(test_query)

if __name__ == "__main__":
    main()