 # SHL Assessment Recommendation System
A production-ready recommendation engine that matches job descriptions to SHL assessments using Hybrid Vector Search and LLM-based Reranking.

## Table of Contents
- [System Architecture](#system-architecture)
- [Key Features](#key-features)
- [Tech Stack](#tech-stack)
- [Installation & Setup](#installation--setup)
- [Usage](#usage)
- [Evaluation & Metrics](#evaluation--metrics)
- [Engineering Decisions](#engineering-decisions)
- [License](#license)

## System Architecture
The system follows a Two-Stage Retrieval Pipeline to balance speed and accuracy:

1. **Candidate Generation (Retrieval)**: Uses ChromaDB and sentence-transformers to perform semantic search across 377+ unique assessments.

2. **Scoring & Ranking (Reranking)**: Employs the Gemini (Gemma-3-4b-it) LLM to evaluate the top candidates against specific job nuances (e.g., time limits, seniority).

## Key Features
- **Semantic Matching**: Understands the context of a Job Description rather than just matching keywords.

- **Robust API**: FastAPI backend with Pydantic validation for seamless integration.

- **Intuitive UI**: Interactive Streamlit dashboard for real-time testing and assessment discovery.

- **Rate-Limit Optimization**: Implemented request throttling and graceful fallbacks for stable batch processing.

## Tech Stack
- **Language**: Python 3.9+

- **Vector DB**: ChromaDB

- **Embeddings**: all-MiniLM-L6-v2 (Sentence-Transformers)

- **LLM**: Google Gemini (Gemma-3-4b-it)

- **API**: FastAPI & Uvicorn

- **Frontend**: Streamlit

- **Deployment Helpers**: pysqlite3-binary (for cloud environment compatibility)

## Installation & Setup
### 1. Clone & Environment
```bash
git clone https://github.com/yourusername/SHL_Recommendation_System.git
cd SHL_Recommendation_System
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 2. Dependencies
```bash
pip install -r requirements.txt
```

### 3. API Configuration
Create a .env file in the root directory:

```
GEMINI_API_KEY=your_key_here
```

## 🛠 Usage
### Rebuilding the Vector Store
If you need to re-index the data (deduplication is handled automatically):

```bash
python src/engine/vector_store.py
```

### Running the API (Port 8000)
```bash
uvicorn src.api.main:app --host 0.0.0.0 --port 8000
```

- Health Check: GET /health

- Recommend: POST /recommend (Body: {"query": "Java Developer"})

### Running the UI (Port 8501)
```bash
streamlit run src/ui/streamlit_app.py
```

## Evaluation & Metrics
The system is optimized for Mean Recall@10.

To generate the final submission CSV for the 9 test queries:

```bash
python evaluations/generate_submission.py
```

- Format: Follows Appendix 3 (Repeated Query, Assessment_url).

- Constraint: Ensures a minimum of 5 and maximum of 10 recommendations per query.

## Engineering Decisions
- **Data Deduplication**: The database was purged and rebuilt to remove duplicate entries, increasing recommendation diversity and Recall@10 accuracy.

- **API Fallback**: Implemented a fallback to raw vector scores when LLM rate limits are hit, ensuring 100% system availability.

- **Batch Processing Throttling**: Added a 15-second delay between test-set queries to accommodate Gemini Free Tier quotas without compromising result quality.

## License
This project is licensed under the MIT License.
