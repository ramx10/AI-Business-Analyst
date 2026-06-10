# AI Business Analyst

An AI-powered business analytics platform that automatically understands datasets, cleans data, analyzes business insights, and generates dashboards and reports using multiple AI agents powered by **Groq + Llama 3.3**.

## Architecture & Tech Stack

This project features a decoupled, professional web architecture:
- **Frontend (`web/`)**: A rich, responsive user interface built using standard HTML5, custom modern CSS, and Vanilla JavaScript (`app.js`), integrating custom UI templates (e.g. *Superieur Admin*).
- **Python REST API (`api/`)**: Built with **FastAPI** to serve the static frontend and expose analytical endpoints powered by **LangChain** and **Groq** (`llama-3.3-70b-versatile`).
- **Java Backend (`backend-java`)**: A **Spring Boot** service that handles authentication, user accounts in PostgreSQL, security configurations, and Google OAuth2 login flows.

## Setup

### 1. Set Up Environment Variables
Create a `.env` file in the root directory:
```env
# Groq LLM API Key
GROQ_API_KEY=your_groq_api_key_here

# Google OAuth2 Credentials
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
```

### 2. Run with Docker Compose
The easiest way to run the entire system is with Docker Compose. This starts PostgreSQL, the Java Spring Boot service, and the Python FastAPI/Web server:
```bash
docker-compose up --build
```
Once started:
- Access the web interface at **`http://localhost:8000`**
- The Java authentication API runs at **`http://localhost:8081`**

### 3. Local Development (Manual Setup)

#### Python FastAPI Backend & Web server:
1. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the FastAPI server:
   ```bash
   uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
   ```
4. Open **`http://localhost:8000`** in your browser.

#### Java Authentication Backend:
1. Make sure PostgreSQL is running on port `5432` with a database named `ai_analyst_db`.
2. Navigate to `backend-java` and run the Spring Boot app:
   ```bash
   ./mvnw spring-boot:run
   ```

## Project Structure

```
AI-Business-Analyst/
│── agents/                  # Multi-agent logic (schema, cleaning, insights, reports)
│── api/                     # FastAPI REST API endpoints & static web mount
│── backend-java/            # Spring Boot security & authentication backend
│── config/                  # Configuration details (LLM initializers)
│── data/                    # Local storage for mock lineage & sharing data
│── reports/                 # Auto-generated reports output directory
│── utils/                   # General data and metric utilities
│── web/                     # Frontend client (HTML, CSS, JS)
│── .env                     # Local configuration keys (ignored by git)
│── Dockerfile               # Production build for Python API & Frontend
│── docker-compose.yml       # Complete multi-container orchestration
│── requirements.txt         # Python library dependencies
```