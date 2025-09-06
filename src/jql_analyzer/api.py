from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
from .chat_participant import JQLAnalyzerParticipant

app = FastAPI()
jql_analyzer = JQLAnalyzerParticipant()

class Query(BaseModel):
    text: str
    context: Dict[str, Any] = {}

@app.post("/analyze")
async def analyze_query(query: Query):
    try:
        # Update context if provided
        if query.context:
            jql_analyzer.update_context(query.context)
        
        # Generate response
        response = await jql_analyzer.generate_response(query.text)
        return response
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
