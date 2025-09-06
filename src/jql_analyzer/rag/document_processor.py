from typing import List, Dict, Any
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from bs4 import BeautifulSoup
import pandas as pd
import json
import os

class DocumentProcessor:
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )

    def process_jira_docs(self, docs_path: str) -> List[Document]:
        """Process JIRA documentation files"""
        documents = []
        
        # Process JQL cheat sheets
        jql_docs = self._process_jql_cheatsheets(f"{docs_path}/jql")
        documents.extend(jql_docs)
        
        # Process JIRA field documentation
        field_docs = self._process_field_docs(f"{docs_path}/fields")
        documents.extend(field_docs)
        
        # Process historical summaries
        history_docs = self._process_historical_data(f"{docs_path}/history")
        documents.extend(history_docs)
        
        return self.text_splitter.split_documents(documents)

    def _process_jql_cheatsheets(self, path: str) -> List[Document]:
        """Process JQL cheat sheets and documentation"""
        documents = []
        
        if not os.path.exists(path):
            return documents

        for filename in os.listdir(path):
            if filename.endswith('.txt') or filename.endswith('.md'):
                with open(os.path.join(path, filename), 'r') as f:
                    content = f.read()
                    documents.append(Document(
                        page_content=content,
                        metadata={
                            "source": filename,
                            "type": "jql_cheatsheet"
                        }
                    ))
                    
        return documents

    def _process_field_docs(self, path: str) -> List[Document]:
        """Process JIRA field documentation"""
        documents = []
        
        if not os.path.exists(path):
            return documents

        for filename in os.listdir(path):
            if filename.endswith('.json'):
                with open(os.path.join(path, filename), 'r') as f:
                    field_data = json.load(f)
                    for field in field_data:
                        content = f"""
                        Field Name: {field.get('name', '')}
                        Field Type: {field.get('type', '')}
                        Description: {field.get('description', '')}
                        Searchable: {field.get('searchable', False)}
                        Operators: {', '.join(field.get('operators', []))}
                        """
                        documents.append(Document(
                            page_content=content,
                            metadata={
                                "source": filename,
                                "type": "field_documentation",
                                "field_name": field.get('name', '')
                            }
                        ))

        return documents

    def _process_historical_data(self, path: str) -> List[Document]:
        """Process historical JIRA data and summaries"""
        documents = []
        
        if not os.path.exists(path):
            return documents

        for filename in os.listdir(path):
            if filename.endswith('.csv'):
                df = pd.read_csv(os.path.join(path, filename))
                
                # Group by common patterns
                summaries = df.groupby(['project', 'issue_type', 'priority']).agg({
                    'summary': lambda x: ' || '.join(x.head(5)),  # Take 5 example summaries
                    'count': 'count'
                }).reset_index()

                for _, row in summaries.iterrows():
                    content = f"""
                    Project: {row['project']}
                    Issue Type: {row['issue_type']}
                    Priority: {row['priority']}
                    Common Patterns:
                    {row['summary']}
                    Frequency: {row['count']} occurrences
                    """
                    documents.append(Document(
                        page_content=content,
                        metadata={
                            "source": filename,
                            "type": "historical_summary",
                            "project": row['project'],
                            "issue_type": row['issue_type']
                        }
                    ))

        return documents
