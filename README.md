# Dailymotion Expert Agent (RAG Assistant)

A Retrieval-Augmented Generation (RAG) assistant that answers questions
using official Dailymotion documentation.

The system:

-   Crawls Dailymotion developer docs
-   Builds semantic embeddings
-   Uses an LLM to generate grounded answers
-   Deploys as a FastAPI service on Google Cloud Run

------------------------------------------------------------------------

## 🧠 Architecture Overview

Docs Crawl → Chunk → Embed → Vector Store → FastAPI → LLM → Answer

------------------------------------------------------------------------

## 📂 Project Structure

agent/ \# Core agent logic\
data/docs_raw/ \# Crawled documentation text files\
embeddings/ \# Vector store (store.pkl)\
logs/ \# Runtime logs (ephemeral in Cloud Run)

api.py \# FastAPI application\
ingest.py \# Documentation crawler\
embed.py \# Embedding generator\
query.py \# Query helper utilities\
requirements.txt \# Dependencies

------------------------------------------------------------------------

## 🚀 Running The Application Locally

### 1. Clone Repository

git clone `<repo-url>`{=html}\
cd `<repo-name>`{=html}

### 2. Create Virtual Environment

python -m venv venv\
source venv/bin/activate

(Windows)\
venv`\Scripts`{=tex}`\activate  `{=tex}

### 3. Install Dependencies

pip install -r requirements.txt

### 4. Set Environment Variables

Create `.env`

GROQ_API_KEY=your_api_key_here

### 5. Run FastAPI Server

uvicorn api:app --reload

### 6. Access Swagger UI

http://localhost:8000/docs

------------------------------------------------------------------------

## 📦 API Endpoint

### POST `/ask`

#### Request

{ "question": "How do I embed a Dailymotion video?", "mode": "developer"
}

#### Response

{ "answer": "...", "confidence": "high", "sources": \["Video Embed"\] }

------------------------------------------------------------------------

# 🔄 Refreshing Documentation & Embeddings

## Step 1 --- Fetch Latest Documentation

python ingest.py

## Step 2 --- Rebuild Embeddings

python embed.py

## Step 3 --- Redeploy Service

gcloud run deploy rag-agent\
--source .\
--region asia-south1\
--allow-unauthenticated\
--memory 2Gi\
--timeout 900

------------------------------------------------------------------------

## Recommended Update Frequency

  Scenario              Frequency
  --------------------- --------------------
  Minor doc changes     Manual
  Regular doc updates   Weekly
  Fast-changing docs    Nightly automation

------------------------------------------------------------------------

# ☁️ Deployment (Google Cloud Run)

### Deploy Command

gcloud run deploy rag-agent\
--source .\
--region asia-south1\
--allow-unauthenticated\
--memory 2Gi

### Set Environment Variables

gcloud run services update rag-agent\
--set-env-vars GROQ_API_KEY=your_key_here\
--region asia-south1

------------------------------------------------------------------------

# ⚠️ Important Notes

## Logs

Cloud Run filesystem is ephemeral. Logs stored in `/logs` are temporary.

## Cold Start

First request may be slower due to model loading.

## Embedding Storage

Embeddings currently ship inside container. Future improvement: Move to
Cloud Storage.

------------------------------------------------------------------------

# 🛠 Development Workflow

Code Change → Test Locally → Deploy Cloud Run\
Docs Update → ingest.py → embed.py → Redeploy

------------------------------------------------------------------------

# 🔐 Security

-   Never commit `.env`
-   Use Cloud Run environment variables
-   Rotate API keys periodically

------------------------------------------------------------------------

# 📌 Future Improvements

-   Persistent vector storage
-   Streaming LLM responses
-   Authentication layer
-   Scheduled ingestion pipeline
-   Observability dashboard

------------------------------------------------------------------------

# 👨‍💻 Author

Maintained by SK
