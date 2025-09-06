from typing import List, Dict, Any, Optional
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from .vector_store import VectorStoreManager

class QueryEngine:
    def __init__(self, vector_store: VectorStoreManager):
        self.vector_store = vector_store
        self.llm = ChatOpenAI(temperature=0)
        self.qa_chain = self._create_qa_chain()

    def _create_qa_chain(self) -> RetrievalQA:
        """Create the QA chain with custom prompt"""
        template = """You are a JIRA Query Language expert. Use the following context and user question to generate a JQL query.
        If you're not sure about the answer, say "I'm not sure" - don't try to make up an answer.
        
        Use the historical patterns and field documentation to construct accurate queries.
        Make sure to use proper field names and operators as shown in the documentation.
        
        Context: {context}
        Question: {question}
        
        JQL Query:"""

        prompt = PromptTemplate(
            template=template,
            input_variables=["context", "question"]
        )

        return RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.vector_store.vectorstore.as_retriever(),
            chain_type_kwargs={"prompt": prompt}
        )

    async def generate_jql_query(self, 
                               query: str, 
                               metadata_filter: Optional[Dict[str, Any]] = None) -> str:
        """Generate JQL query from natural language"""
        # Get relevant context with metadata filtering
        context = self.vector_store.get_relevant_context(query, metadata_filter)
        
        # Generate JQL query
        response = self.qa_chain.run(
            question=query,
            context=context
        )
        
        return response

    def update_context(self, new_documents: List[Any]) -> None:
        """Update the vector store with new documents"""
        self.vector_store.add_documents(new_documents)
        # Recreate the QA chain with updated vector store
        self.qa_chain = self._create_qa_chain()
