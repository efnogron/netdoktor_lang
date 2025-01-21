from typing import Dict, Any
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from langchain_chroma import Chroma

from retrieval_graph.state import RetrievalState
from retrieval_graph.configuration import RetrievalConfiguration
from retrieval_graph.prompts import QUERY_ANALYSIS_PROMPT, RESULT_SYNTHESIS_PROMPT
from shared.utils import setup_embeddings

def create_retrieval_graph(config: RetrievalConfiguration) -> StateGraph:
    """Create the retrieval workflow graph."""
    
    # Initialize components
    embeddings = setup_embeddings(config.embedding_model)
    vectorstore = Chroma(
        collection_name="guidelines",
        embedding_function=embeddings
    )
    llm = ChatOpenAI(model=config.llm_model)
    
    # Define graph nodes
    def search_node(state: RetrievalState) -> Dict[str, Any]:
        """Perform semantic search."""
        results = vectorstore.similarity_search(
            state.query,
            k=config.top_k,
        )
        return {"results": results}
    
    def synthesize_node(state: RetrievalState) -> Dict[str, Any]:
        """Synthesize results into a coherent response."""
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