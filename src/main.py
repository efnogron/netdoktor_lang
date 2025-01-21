import os
from pathlib import Path
from dotenv import load_dotenv
from typing import List, Dict, Any
import json
from datetime import datetime

from index_graph.configuration import IndexConfiguration
from index_graph.state import IndexState
from index_graph.graph import graph as index_graph

from retrieval_graph.configuration import RetrievalConfiguration
from retrieval_graph.state import RetrievalState
from retrieval_graph.graph import graph as retrieval_graph

from query_formation.processor import QueryFormationProcessor
from query_formation.configuration import QueryFormationConfig

from shared.output_formatter import format_verification_results


# Load environment variables
load_dotenv()

def index_guidelines():
    """Index the medical guidelines."""
    print("Starting indexing process...")
    
    # Get the absolute path to the project root
    project_root = Path(__file__).parent.parent
    
    # Configure indexing
    config = IndexConfiguration(
        collection_name="guidelines",  # Use consistent name
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

def process_and_verify_claims(input_file: Path, max_sentences: int = None) -> None:
    """Process medical text and verify claims against guidelines."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_dir = Path("results") / timestamp
    results_dir.mkdir(parents=True, exist_ok=True)
    
    print("\nStarting medical text analysis and verification...")
    
    # Initialize configurations
    query_config = QueryFormationConfig(max_sentences=max_sentences)
    retrieval_config = RetrievalConfiguration()
    
    # Process text to extract claims
    processor = QueryFormationProcessor(query_config)
    claims = processor.process_markdown_sections(input_file)
    
    # Verify each claim and store results
    verified_claims = []
    for idx, claim in enumerate(claims, 1):
        print(f"\nVerifying claim {idx}/{len(claims)}: {claim['query']}")
        
        # Get relevant guidelines through RAG
        retrieval_result = search_guidelines(claim['query'])
        
        result = {
            "original_sentence": claim['sentence'],
            "context_paragraph": claim['context']['paragraph'],
            "verification_query": claim['query'],
            "retrieved_chunks": retrieval_result.get('chunks', []),
            "verification_result": retrieval_result.get('verification', {})
        }
        
        verified_claims.append(result)
        
        # Save individual result
        with open(results_dir / f"claim_{idx}.json", 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
    
    # Save summary
    summary = {
        "total_claims": len(verified_claims),
        "timestamp": timestamp,
        "input_file": str(input_file),
        "max_sentences": max_sentences
    }
    
    with open(results_dir / "summary.json", 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    
    print(f"\nAnalysis complete! Results saved to: {results_dir}")
    
    # Format and display results
    format_verification_results(results_dir)

def search_guidelines(query: str) -> Dict[str, Any]:
    """Search medical guidelines for verification."""
    try:
        print(f"\nSearching guidelines for: {query}")
        
        # Initialize state with the query
        state = RetrievalState(query=query)
        
        # Execute the pre-compiled graph
        result = retrieval_graph.invoke(state)
        
        # Extract results and include detailed chunk information
        chunks_info = []
        if "results" in result:
            print(f"Processing {len(result['results'])} retrieved chunks")
            for doc in result["results"]:
                chunk_info = {
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "score": doc.metadata.get("score", None)
                }
                chunks_info.append(chunk_info)
        else:
            print("WARNING: No 'results' key in graph output")
            
        return {
            "chunks": chunks_info,
            "verification": {
                "status": "SUCCESS",
                "messages": [str(msg.content) for msg in result["messages"]] if "messages" in result else []
            }
        }
        
    except Exception as e:
        print(f"Search failed with error: {str(e)}")
        return {
            "chunks": [],
            "verification": {
                "status": "ERROR",
                "reason": str(e)
            }
        }

def main():
    """Main execution function."""
    # Get command line arguments
    import argparse
    parser = argparse.ArgumentParser(description='Process and verify medical claims.')
    parser.add_argument('--max-sentences', type=int, help='Maximum number of sentences to process')
    args = parser.parse_args()
    
    # First, index the guidelines if needed
    index_guidelines()
    
    # Process and verify claims
    project_root = Path(__file__).parent.parent
    article_path = project_root / "input" / "asthma" / "article" / "article.md"
    
    process_and_verify_claims(
        input_file=article_path,
        max_sentences=args.max_sentences
    )

if __name__ == "__main__":
    main()