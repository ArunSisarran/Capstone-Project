from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth

app = FastAPI(title="Recipe Recommender API")

origins = [
  "http://localhost:3000",
  "http://localhost:5173"
]

app.add_middleware(
  CORSMiddleware,
  allow_origins=origins,
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"]
)
app.include_router(auth.router)

@app.get("/health")
def health_check():
  return {"status": "ok"}