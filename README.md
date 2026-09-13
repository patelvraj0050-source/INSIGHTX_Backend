# INSIGHTX v0.2 — Data Engineering Layer

**Business Intelligence & Analytics Platform**  
**Built by VRAJ PATEL**

> “Turning data into insight, and insight into better decisions.”

## v0.2 capabilities
- PostgreSQL integration with environment-based configuration
- Reusable ETL: Extract → Transform → Validate → Load
- Data-quality validation and quality score
- Star schema: `fact_sales`, `dim_date`, `dim_customer`, `dim_product`, `dim_region`
- SQL analytics layer
- Docker Compose PostgreSQL for local development
- Data Engineering workspace integrated into the v0.1.3 premium UI
- Demo mode still works without PostgreSQL
- Existing analytics, BI intelligence, and upload experience preserved

## Quick start
```bash
pip install -r requirements.txt
streamlit run app.py
```

## PostgreSQL mode
```bash
docker compose up -d
```
Set:
```text
INSIGHTX_DATABASE_URL=postgresql+psycopg2://insightx:insightx@localhost:5432/insightx
```
Then run Streamlit, upload a dataset, open **Data Engineering**, and load the clean data into the warehouse.

## Architecture
```text
Upload
  ↓
Extract → Transform → Validate
  ↓
PostgreSQL Star Schema
  ↓
SQL Analytics
  ↓
BI / KPI / Insights
  ↓
INSIGHTX Experience UI
```

## v0.3 — Advanced Analytics
- Statistical anomaly detection using configurable z-scores
- Monthly trend forecasting with transparent linear baseline
- Simple linear regression with R², slope, intercept and sample count
- Segment-level descriptive statistics
- New **Advanced Analytics Lab** workspace tab

## v0.4 — Professional BI Layer
- KPI hierarchy across financial, operational, and profitability measures
- Contribution analysis with ranking, share, and cumulative share
- Executive summary statements derived from detected business fields
- Transparent decision recommendations with priority labels
- New **BI Command Center** workspace tab
- Existing v0.3 advanced analytics and v0.2 data engineering features preserved


## v0.5 — AI Business Analyst

The new **AI Business Analyst** tab accepts natural-language questions and maps
them to deterministic analytics over the uploaded dataset. It includes:
- Overview questions
- Regional performance
- Top products/categories
- Monthly revenue change
- Profitability
- Anomaly detection

The assistant reports its detected intent, confidence, answer, and evidence.
It does not fabricate values or require an external AI API key.


## Royal Amber Animated UI

This build adds a black/charcoal/gold visual system with:
- Animated page entrances and KPI hover states
- Gold animated progress bars
- Animated dataset drop-zone styling
- Royal Amber cursor styling
- Premium glass-like panels and gold accents
- Reduced-motion accessibility support


## v0.6 — Production Engineering & Deployment

This release adds a production-oriented FastAPI service while preserving the
existing Streamlit experience.

### API endpoints

- `GET /health` — service health check
- `POST /dataset/upload` — upload a CSV dataset
- `GET /dataset` — inspect the loaded dataset
- `POST /analyst/ask` — ask a verified business question

Interactive API documentation is available at:

- `http://localhost:8000/docs`

### Run the complete stack with Docker

From the project directory:

```cmd
docker compose -f docker-compose.production.yml up --build -d
```

Open:

- Streamlit frontend: `http://localhost:8501`
- FastAPI documentation: `http://localhost:8000/docs`
- API health: `http://localhost:8000/health`

Stop the stack:

```cmd
docker compose -f docker-compose.production.yml down
```

The PostgreSQL volume is preserved unless you explicitly remove it.

### Run tests locally

```cmd
pytest -q
```

### Deployment note

This package is deployment-ready for a Docker host. A public cloud deployment
still requires a hosting provider, domain, secrets, and environment-specific
configuration.
