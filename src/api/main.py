import os
import sys
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# This is the "Bouncer" that allows everyone in
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all domains (recruiter's tools, your streamlit, etc.)
    allow_credentials=True,
    allow_methods=["*"],  # Allows GET, POST, etc. [cite: 157, 166]
    allow_headers=["*"],  # Allows all headers
)

# Add project root to path for imports
proj_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if proj_root not in sys.path:
    sys.path.insert(0, proj_root)

from src.engine.retriever import Retriever
from src.engine.llm_handler import LLMHandler

app = FastAPI(title="SHL Assessment Recommendation System")

# Initialize engine components
try:
    print("Initializing Search Engine...")
    retriever = Retriever()
    llm_handler = LLMHandler()
    print("Search Engine Initialized Successfully!")
except Exception as e:
    print(f"Error initializing search engine: {e}")
    retriever = None
    llm_handler = None

class QueryRequest(BaseModel):
    """Request model for assessment recommendations."""
    query: str

@app.get("/health")
def health_check():
    """Health check endpoint to verify system status."""
    if retriever and llm_handler:
        return {"status": "healthy"}
    else:
        return {"status": "unhealthy", "detail": "Engine failed to initialize"}

@app.post("/recommend")
def recommend_assessment(request: QueryRequest):
    """
    Get assessment recommendations based on a query.

    Returns a list of recommended assessments ranked by relevance.
    """
    if not retriever or not llm_handler:
        raise HTTPException(status_code=503, detail="Engine is unavailable")

    user_query = request.query
    print(f"User Query: {user_query}")

    # Get initial results from vector search
    results = retriever.search(user_query, n_results=100)
    # Rerank results using LLM
    final_results = llm_handler.rerank(user_query, results)

    formatted_recommendations = []
    for item in final_results:
        raw_type = item.get('test_type', "[]")

        # Process test_type to ensure consistent format
        if isinstance(raw_type, str):
            # Clean string by removing brackets and quotes
            clean_str = raw_type.replace("[", "").replace("]", "").replace("'", "").replace('"', "")
            # Split by comma and clean whitespace
            t_type = clean_str.split(",")
            t_type = [t.strip() for t in t_type if t.strip()]
        else:
            # Use raw_type directly if it's already a list
            t_type = raw_type

        # Ensure t_type is always a list
        if not isinstance(t_type, list):
            t_type = [str(t_type)]

        # Format the recommendation with all required fields
        formatted_recommendations.append({
            "url": item.get("url", ""),
            "name": item.get("name", "Unknown"),
            "adaptive_support": item.get("adaptive_support", "No"),
            "description": item.get("description", ""),
            "duration": int(float(item.get("duration", 0))),
            "remote_support": item.get("remote_support", "No"),
            "test_type": t_type
        })

    return {"recommended_assessments": formatted_recommendations}

if __name__ == "__main__":
    print("Starting API Server on http://127.0.0.1:8001")
    uvicorn.run(app, host="127.0.0.1", port=8001)
