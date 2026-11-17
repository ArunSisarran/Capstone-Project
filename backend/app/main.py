from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, recipes, saved_recipes, dietary_tags, ingredients, users, scan
from slowapi.errors import RateLimitExceeded
from fastapi.responses import JSONResponse
from app.core.limiter import limiter
from app.core.config import settings

app = FastAPI(title="Recipe Recommender API")

origins = [origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()]

app.add_middleware(
  CORSMiddleware,
  allow_origins=origins,
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"]
)
for router in (auth.router, recipes.router, saved_recipes.router, dietary_tags.router, ingredients.router, users.router, scan.router):
    app.include_router(router)

app.state.limiter = limiter

@app.exception_handler(RateLimitExceeded)
def rate_limit_exceeded(request, exc):
   return JSONResponse(status_code=429, content={"detail": "Too many requests. Wait a little and try again."})

@app.get("/health")
def health_check():
  return {"status": "ok"}