
# INSIGHTX v0.6.1 — Public Render Deployment

## 1. Push the project to GitHub

Create a repository and upload the contents of this project folder.

Do not upload:
- `.env`
- database passwords
- API keys
- `.venv`
- uploaded customer datasets containing private information

## 2. Deploy with Render Blueprint

1. Open Render.
2. Choose **New → Blueprint**.
3. Connect the GitHub repository.
4. Select the repository containing `render.yaml`.
5. Review the services.
6. Apply the blueprint.

The blueprint creates:

- `insightx-api` — FastAPI backend
- `insightx-frontend` — Streamlit frontend
- `insightx-db` — PostgreSQL database

## 3. Public URLs

After deployment, the expected URLs are:

- Frontend: `https://insightx-frontend.onrender.com`
- API: `https://insightx-api.onrender.com`
- API docs: `https://insightx-api.onrender.com/docs`
- Health check: `https://insightx-api.onrender.com/health`

Render may assign a different URL if a name is unavailable. Use the actual URLs shown in the Render dashboard.

## 4. Important production notes

- The current AI Business Analyst API keeps its uploaded dataset in process memory.
- Restarting or redeploying the API clears that in-memory dataset.
- For a fully production-grade release, datasets should be stored in PostgreSQL or object storage.
- Configure `INSIGHTX_ALLOWED_ORIGINS` with the exact frontend URL after Render creates it.
- The PostgreSQL service may incur charges depending on the selected Render plan.
- Do not expose database credentials in source code or GitHub.

## 5. Manual service deployment alternative

If you do not want to use a Blueprint:

### API service

Build command:

```bash
pip install -r requirements.txt
```

Start command:

```bash
uvicorn backend.main:app --host 0.0.0.0 --port $PORT
```

### Frontend service

Build command:

```bash
pip install -r requirements.txt
```

Start command:

```bash
streamlit run app.py --server.address 0.0.0.0 --server.port $PORT
```

## 6. Verify deployment

Open:

```text
https://insightx-api.onrender.com/health
```

Then open:

```text
https://insightx-api.onrender.com/docs
```

Finally open the frontend URL and test dataset upload and dashboard loading.
