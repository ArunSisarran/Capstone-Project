from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, recipes, saved_recipes, dietary_tags, ingredients, users

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
for router in (auth.router, recipes.router, saved_recipes.router, dietary_tags.router, ingredients.router, users.router):
    app.include_router(router)


@app.get("/health")
def health_check():
  return {"status": "ok"}