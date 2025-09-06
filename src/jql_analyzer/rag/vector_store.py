from typing import List, Dict, Any, Optional
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.docstore.document import Document

class VectorStoreManager:
    def __init__(self, persist_directory: str):
        self.persist_directory = persist_directory
        self.embeddings = OpenAIEmbeddings()
        self.vectorstore = None

    def initialize_vectorstore(self, documents: List[Document]) -> None:
        """Initialize or update vector store with documents"""
        self.vectorstore = Chroma.from_documents(
            documents=documents,
            embedding=self.embeddings,
            persist_directory=self.persist_directory
        )
        self.vectorstore.persist()

    def search(self, query: str, k: int = 5, filter_metadata: Optional[Dict[str, Any]] = None) -> List[Document]:
        """Search for relevant documents"""
        if not self.vectorstore:
            raise ValueError("Vector store not initialized")
            
        return self.vectorstore.similarity_search(
            query=query,
            k=k,
            filter=filter_metadata
        )

    def add_documents(self, documents: List[Document]) -> None:
        """Add new documents to the vector store"""
        if not self.vectorstore:
            self.initialize_vectorstore(documents)
        else:
            self.vectorstore.add_documents(documents)
            self.vectorstore.persist()

    def get_relevant_context(self, query: str, metadata_filters: Optional[Dict[str, Any]] = None) -> str:
        """Get relevant context for a query"""
        relevant_docs = self.search(query, filter_metadata=metadata_filters)
        
        # Combine relevant documents into context
        context = "\n\n".join([
            f"Source: {doc.metadata.get('source', 'Unknown')}\n"
            f"Type: {doc.metadata.get('type', 'Unknown')}\n"
            f"{doc.page_content}"
            for doc in relevant_docs
        ])
        
        return context
