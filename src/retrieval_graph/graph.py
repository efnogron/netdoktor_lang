from typing import Dict, Any
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from langchain_chroma import Chroma

from retrieval_graph.state import RetrievalState
from retrieval_graph.configuration import RetrievalConfiguration
from retrieval_graph.prompts import RESULT_SYNTHESIS_PROMPT
from shared.utils import setup_embeddings

def create_retrieval_graph(config: RetrievalConfiguration) -> StateGraph:
    """Create the retrieval workflow graph."""
    
    # Initialize components
    embeddings = setup_embeddings(config.embedding_model)
    vectorstore = Chroma(
        collection_name=config.collection_name,
        embedding_function=embeddings,
        persist_directory=str(config.vector_store_dir)
    )
    
    print(f"\nInitialized vector store from {config.vector_store_dir}")
    print(f"Collection name: {config.collection_name}")
    print(f"Collection size: {vectorstore._collection.count()}")
    
    llm = ChatOpenAI(model=config.llm_model)
    
    # Define graph nodes
    def search_node(state: RetrievalState) -> Dict[str, Any]:
        """Perform semantic search."""
        print(f"\nExecuting search for query: {state.query}")
        
        try:
            results = vectorstore.similarity_search_with_score(
                state.query,
                k=config.top_k,
            )
            
            # Unpack results and scores
            docs = []
            print(f"Found {len(results)} results:")
            for doc, score in results:
                print(f"- Score {score:.3f}: {doc.page_content[:100]}...")
                doc.metadata["score"] = score
                docs.append(doc)
                
            if not docs:
                print("WARNING: No documents found in search!")
                
            return {"results": docs}
            
        except Exception as e:
            print(f"Search error: {str(e)}")
            return {"results": []}
    
    def synthesize_node(state: RetrievalState) -> Dict[str, Any]:
        """Synthesize results into a coherent response."""
        if not state.results:
            print("Keine relevanten Leitlinien gefunden")
            return {"messages": ["Keine relevanten Leitlinien gefunden."]}
            
        print(f"Analysiere {len(state.results)} Ergebnisse")
        context = "\n\n".join(doc.page_content for doc in state.results)
        response = llm.invoke(
            RESULT_SYNTHESIS_PROMPT.format(
                query=state.query,
                context=context
            )
        )
        return {"messages": [response]}
    
    # Create and compile graph
    workflow = StateGraph(RetrievalState)
    
    # Add nodes
    workflow.add_node("search", search_node)
    workflow.add_node("synthesize", synthesize_node)
    
    # Add edges
    workflow.add_edge(START, "search")
    workflow.add_edge("search", "synthesize")
    workflow.add_edge("synthesize", END)
    
    return workflow.compile()

# Create the default graph instance
graph = create_retrieval_graph(RetrievalConfiguration()) 