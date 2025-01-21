from pathlib import Path
from typing import List
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

def load_and_split_pdf(
    file_path: Path,
    chunk_size: int = 1000,
    chunk_overlap: int = 100
) -> List[Document]:
    """Load and chunk a PDF document.
    
    Args:
        file_path: Path to the PDF file
        chunk_size: Size of text chunks
        chunk_overlap: Overlap between chunks
        
    Returns:
        List of document chunks
        
    Example:
        >>> chunks = load_and_split_pdf(Path("guideline.pdf"))
        >>> print(f"Created {len(chunks)} chunks")
    """
    loader = PyPDFLoader(str(file_path))
    documents = loader.load()
    
    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    
    chunks = text_splitter.split_documents(documents)
    print(f"Created {len(chunks)} chunks from {file_path.name}")
    return chunks 