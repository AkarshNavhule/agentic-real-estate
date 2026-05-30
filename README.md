# REAL ESTATE AI CHATBOT

An enterprise-grade, full-stack AI Real Estate Assistant built using **FastAPI**, **React (Tailwind CSS)**, and **Microsoft Semantic Kernel**. The platform leverages Retrieval-Augmented Generation (RAG) to query property listings via Azure AI Search, integrates directly with an SQLite CRM database for tour schedules, maintains fluid session-based conversation memory, and delivers token-by-token streaming responses using Server-Sent Events (SSE).

---

## 🏗️ What Was Built: Features & Architecture

The system is split into an asynchronous Python backend and a reactive single-page frontend:

### 1. Backend AI Engine (FastAPI & Semantic Kernel)
* **Orchestration Engine:** Powered by Microsoft Semantic Kernel to manage structured prompts, execution settings, and multi-agent native function execution.
* **Hybrid RAG Architecture:** Vector and keyword indexing via Azure AI Search to pull rich, factual property context matching user queries.
* **Native Plugin System:** An automated `PropertyManagementPlugin` that interfaces with an SQLite CRM database to dynamically fetch real-time agent allocations and tour timetables.
* **Dual-Delivery APIs:** Features both a standard blocking JSON endpoint (`/chat`) and an optimized Server-Sent Events endpoint (`/chat/stream`) yielding token-by-token streaming response generation.
* **In-Memory Session Manager:** Tracks thread-isolated context buffers using unique session tokens passed via custom HTTP request bodies and response headers (`X-Session-ID`), automatically pruning histories past a set token horizon to optimize LLM performance.

### 2. Frontend Interface (React & Tailwind CSS)
* **Fluid Streaming UI:** Implements JavaScript's asynchronous generator structures and the Stream Reader API to parse incoming binary streams into real-time visual output.
* **Contextual Continuity Control:** Seamlessly captures, stores, and presents unique session tokens, providing users with a "Reset Chat" utility to instantly clear memory context and establish a new conversational state.

---

## 🛠️ Tech Stack

* **Backend:** Python 3.11+, FastAPI, Microsoft Semantic Kernel, Pydantic v2, Uvicorn
* **Frontend:** React 18+, Tailwind CSS, Fetch Stream API
* **Data & Search:** Azure OpenAI (GPT-4o/GPT-4-turbo), Azure AI Search, SQLite3
# --- Server Configurations ---
PORT=8000
HOST=0.0.0.0

# --- Azure OpenAI Service Credentials ---
AZURE_OPENAI_API_KEY=your-azure-openai-api-key
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
AZURE_OPENAI_CHAT_DEPLOYMENT=your-gpt-4o-deployment-name

# --- Azure AI Search Service Credentials ---
AZURE_SEARCH_ENDPOINT=https://your-search-service-name.search.windows.net
AZURE_SEARCH_KEY=your-admin-or-query-api-key
AZURE_SEARCH_INDEX=realestate-properties-index

# --- Local Infrastructure ---
DATABASE_URL=sqlite:///./crm.db
💻 Local Development Setup
1. Running the FastAPI Backend
Navigate to your backend directory, set up a virtual environment, and run the server:

Bash
cd backend

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Launch the application via Uvicorn
uvicorn app.main:app --reload --port 8000
The interactive Swagger API documentation will be accessible at: http://localhost:8000/docs

2. Running the React Frontend
Navigate to your frontend directory, install the packages, and spin up the development engine:

Bash
cd frontend

# Install Node modules
npm install

# Start the Vite / Create-React-App environment
npm run dev
Open your browser to the local address displayed (typically http://localhost:5173 or http://localhost:3000).

🐳 Dockerization (Local Container Testing)
To package your application into isolated containers, you can use the multi-container configuration below.

1. backend/Dockerfile
Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
2. Root Directory docker-compose.yml
YAML
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    env_file:
      - ./backend/.env
    volumes:
      - ./backend:/app

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - CHOKIDAR_USECHALLENGE=true
    stdin_open: true
    tty: true
Run the entire cluster locally with a single command:

Bash
docker-compose up --build
☁️ Azure Production Deployment Strategy
To run your full-stack containerized agent in production at scale, deploy it to Azure Container Apps (ACA) via Azure Container Registry (ACR).

[ Developer Git Push ] ──> [ Azure Container Registry (ACR) ]
                                    │
                                    ▼
                     [ Azure Container Apps (ACA) ]
                     ├── Backend Container (Port 8000)
                     └── Frontend Container (Port 3000)
Step 1: Login and Authenticate Azure CLI
Bash
az login
az account set --subscription "Your-Subscription-Name"
Step 2: Create Azure Container Registry (ACR)
Bash
# Create a resource group
az group create --name realestate-agent-rg --location eastus

# Create an Azure Container Registry instance
az acr create --resource-group realestate-agent-rg --name realestateregistry --sku Basic
Step 3: Build and Push Images to ACR
Bash
# Authenticate local Docker daemon to your Azure registry
az acr login --name realestateregistry

# Tag and Push Backend Image
docker build -t realestateregistry.azurecr.io/agent-backend:v1 ./backend
docker push realestateregistry.azurecr.io/agent-backend:v1

# Tag and Push Frontend Image
docker build -t realestateregistry.azurecr.io/agent-frontend:v1 ./frontend
docker push realestateregistry.azurecr.io/agent-frontend:v1
Step 4: Deploy to Azure Container Apps
Bash
# Create the Container Apps environment
az containerapp env create --name realestate-env --resource-group realestate-agent-rg --location eastus

# Deploy Backend Container (Exposed Internally or Externally for API consumption)
az containerapp create \
  --name agent-backend \
  --resource-group realestate-agent-rg \
  --environment realestate-env \
  --image realestateregistry.azurecr.io/agent-backend:v1 \
  --target-port 8000 \
  --ingress external \
  --env-vars AZURE_OPENAI_API_KEY="your-key" AZURE_SEARCH_ENDPOINT="your-endpoint" # add remaining variables

# Deploy Frontend Container
az containerapp create \
  --name agent-frontend \
  --resource-group realestate-agent-rg \
  --environment realestate-env \
  --image realestateregistry.azurecr.io/agent-frontend:v1 \
  --target-port 3000 \
  --ingress external
🧠 Key Engineering Insights & Learnings
Semantic Kernel Orchestration: Moving beyond basic string formatting wrappers to native AI orchestration framework engines allows for decoupled, reusable tools and structured planning execution blocks.

Asynchronous Generator Management: Realized that managing true streaming mechanics requires handling data streams differently: yielding single tokens downstream immediately for UX performance while buffering full string aggregates to commit into system memory layers at the end of the generator loop.

The CORS Custom Header Trap: Encountered and solved cross-origin network header filtering. Standard security boundaries mask non-standard headers (X-Session-ID) from single-page web applications unless explicitly exposed through the host application backend's expose_headers CORS middleware options.

Token Horizon Management: Learned to actively slice and manage the in-memory array (history[-6:]) to prevent context window bloat, ensuring steady request response latencies and controlling runtime operational costs.