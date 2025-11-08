# Adaptive Feature Compression System (AFCS)

AFCS is a self-learning dimensionality reduction and feature ranking framework. Upload a CSV to clean, rank, compress, visualise, and export reproducible pipelines locally.

## Features
- FastAPI backend with PCA and autoencoder compression
- Feature scoring combining variance, PCA loadings, and redundancy penalties
- Plot generation for feature importance, correlation, latent space, and reconstruction error
- Next.js frontend with responsive Aurora Neo design system
- Docker Compose one-command startup
- CI pipeline running backend and frontend tests

## Getting started

### Prerequisites
- Python 3.11+
- Node.js 20+
- Docker (optional for containerised run)

### Local development
```bash
cd afcs
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
cd frontend
npm install
```

Start services in split terminals:
```bash
# Backend
cd afcs/backend
uvicorn main:app --reload

# Frontend
cd afcs/frontend
npm run dev
```

Visit http://localhost:3000 and upload a CSV.

### Docker compose
```bash
cd afcs
docker compose up --build
```

Frontend runs on http://localhost:3000, API on http://localhost:8000.

### Running tests
```bash
cd afcs/backend
pytest

cd ../frontend
npm test -- --run
```

### CI
GitHub Actions workflow `.github/workflows/ci.yml` installs dependencies and runs tests for both backend and frontend on every push or pull request.

## Project structure
```
afcs/
  backend/
    afcs_core/
    main.py
  frontend/
    app/
    components/
    lib/
  shared/
  docker/
  docker-compose.yml
```

## Data privacy
Uploads never leave your machine. Artifacts are stored under `./data` and may be removed by deleting result entries via the API.

## License
MIT
