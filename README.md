# Capstone-Project

## Local demo (SQLite, one machine)

One-time setup, from the repo root:

```sh
python3 -m venv venv
venv/bin/pip install -r backend/requirements.txt -r VisionModel/requirements.txt certifi
(cd frontend && npm ci)
```

- `backend/.env`: `DATABASE_URL=sqlite:///./demo.db`, a random `SECRET_KEY`, `FRONTEND_URL=http://localhost:5173`, `VISION_URL=http://localhost:8001`
- `VisionModel/.env`: `GEMINI_API_KEY=...`

Create and fill the database (run from `backend/`):

```sh
../venv/bin/python -c "from app.core.database import Base, engine; import app.models.models; Base.metadata.create_all(engine)"
SSL_CERT_FILE=$(../venv/bin/python -m certifi) ../venv/bin/python -m scripts.import_themealdb --commit --yes
```

Then `./demo.sh` starts everything; open http://localhost:5173. Ctrl-C stops it.
