# AI Business Analyst

An AI-powered business analytics platform that automatically understands datasets, cleans data, analyzes business insights, and generates dashboards and reports using multiple AI agents powered by **Groq + Llama 3.3**.

## Features

- Automated schema detection and analysis
- Data quality & cleaning analysis
- KPI generation
- AI-generated business insights and executive reports
- Interactive visualizations (Bar, Line, Pie, Histogram, Box Plot, Heatmap)
- Multi-agent pipeline (Schema → Cleaning → KPI → Insights → Report)
- Large dataset handling (50k+ rows)

## Tech Stack

- **Python**
- **Streamlit** — interactive dashboard UI
- **LangChain + LangChain-Groq** — LLM orchestration
- **Groq API** (`llama-3.3-70b-versatile`) — AI inference
- **Pandas** — data manipulation
- **Plotly** — interactive charts

## Setup

1. **Clone the repo and create a virtual environment**

```bash
python -m venv .venv
.venv\Scripts\activate
```

2. **Install dependencies**

```bash
pip install -r requirements.txt
```

3. **Configure your Groq API key**

Create a `.env` file in the project root:

```
GROQ_API_KEY=your_groq_api_key_here
```

4. **Run the dashboard**

```bash
.venv\Scripts\streamlit.exe run dashboard/app.py
```

## Project Structure

```
AI-Business-Analyst/
│── agents/                  # AI agents (schema, cleaning, KPI, insights, report, visualization)
│── config/
│   └── llm.py               # Groq LLM initialisation
│── dashboard/
│   ├── app.py               # Streamlit entry point
│   ├── charts.py            # Chart helpers
│   ├── metrics.py           # Metric helpers
│   └── pages/               # Streamlit multi-page app pages
│── reports/
│   └── report_generator.py  # Save AI reports to disk
│── utils/
│   ├── helper.py            # General utilities (CSV reading, etc.)
│   ├── chart_utils.py       # Reusable Plotly chart builders
│   └── metrics.py           # DataFrame metric helpers
│── .env                     # GROQ_API_KEY (not committed)
│── requirements.txt
│── main.py
```