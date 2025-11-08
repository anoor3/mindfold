# Architecture overview

```
+-----------------+          +---------------------+          +--------------------+
|  Next.js UI     |  Fetch   | FastAPI backend     |  Calls   | AFCS core modules  |
|  (frontend/)    +--------->| (backend/main.py)   +--------->| preprocessing,     |
|  - Upload flow  |          | - Upload/Analyze    |          | ranking, PCA/AE,   |
|  - Analysis UI  |          | - Compress jobs     |          | clustering, plots  |
|  - Results view |          | - Static plots      |          |                    |
+-----------------+          +---------------------+          +--------------------+
                                      |
                                      v
                              Local data storage
                              (./data uploads, artifacts, plots)
```

## Backend
- `afcs_core/preprocessing.py` handles CSV loading, missing data, encoding, and scaling.
- `afcs_core/ranking.py` computes composite feature importance scores.
- `afcs_core/pca_model.py` and `ae_model.py` provide compression implementations.
- `afcs_core/pipeline.py` orchestrates jobs, clustering, visualisation, and artifact export.
- `main.py` exposes REST endpoints with job polling and artifact downloads.

## Frontend
- Next.js App Router with pages for landing, upload, analysis, results, and help.
- TanStack Query manages API calls, React Hook Form handles upload options, Plotly renders charts.
- Theme and accessibility handled by Aurora Neo design tokens and keyboard shortcuts.

## DevOps
- Dockerfiles for backend and frontend containers.
- `docker-compose.yml` for one-command startup with shared `./data` volume.
- GitHub Actions workflow runs backend pytest and frontend vitest suites.
