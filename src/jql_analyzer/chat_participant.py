from typing import List, Dict, Any
from jira import JIRA
import os
from dotenv import load_dotenv
from .rag.document_processor import DocumentProcessor
from .rag.vector_store import VectorStoreManager
from .rag.query_engine import QueryEngine

class JQLAnalyzerParticipant:
    def __init__(self):
        load_dotenv()
        self.name = "YOUR JQL ANALYZER"
        self.jira = self._init_jira()
        
        # Initialize RAG components
        self.doc_processor = DocumentProcessor()
        self.vector_store = VectorStoreManager("./data/chroma_db")
        self.query_engine = QueryEngine(self.vector_store)
        
        # Process and load initial documents
        self._initialize_rag()

    def _init_jira(self) -> JIRA:
        """Initialize JIRA client"""
        return JIRA(
            server=os.getenv('JIRA_SERVER'),
            basic_auth=(os.getenv('JIRA_EMAIL'), os.getenv('JIRA_API_TOKEN'))
        )

    def _init_jira(self) -> JIRA:
        """Initialize JIRA client"""
        return JIRA(
            server=os.getenv('JIRA_SERVER'),
            basic_auth=(os.getenv('JIRA_EMAIL'), os.getenv('JIRA_API_TOKEN'))
        )

    def _initialize_rag(self) -> None:
        """Initialize RAG system with documents"""
        # Process documents
        docs = self.doc_processor.process_jira_docs("./data/docs")
        
        # Initialize vector store
        self.vector_store.initialize_vectorstore(docs)

    async def generate_response(self, query: str) -> Dict[str, Any]:
        """Generate response for user query"""
        try:
            # Generate JQL query using RAG system
            jql_response = await self.query_engine.generate_jql_query(query)
            
            # Execute JQL query if valid
            if "I'm not sure" not in jql_response:
                jira_results = self.jira.search_issues(jql_response, maxResults=10)
                
                return {
                    "status": "success",
                    "jql_query": jql_response,
                    "results": [
                        {
                            "key": issue.key,
                            "summary": issue.fields.summary,
                            "status": issue.fields.status.name,
                            "assignee": issue.fields.assignee.displayName if issue.fields.assignee else "Unassigned",
                            "priority": issue.fields.priority.name if issue.fields.priority else "None",
                            "created": issue.fields.created,
                            "updated": issue.fields.updated
                        }
                        for issue in jira_results
                    ]
                }
            else:
                return {
                    "status": "unclear",
                    "message": "I couldn't generate a JQL query for your request. Could you please rephrase or provide more details?"
                }

        except Exception as e:
            return {
                "status": "error",
                "message": f"Error processing query: {str(e)}"
            }

    def update_context(self, context: Dict[str, Any]) -> None:
        """Update conversation context and RAG system"""
        # Process any new documents in the context
        if 'new_docs' in context:
            new_docs = self.doc_processor.process_jira_docs(context['new_docs'])
            self.query_engine.update_context(new_docs)
