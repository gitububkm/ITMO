import logging
from fastapi import FastAPI
from .api.router import api_router

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

app = FastAPI(title="News CRUD API")

@app.get("/")
async def root():
    return {"status": "ok", "message": "Welcome to News CRUD API"}

app.include_router(api_router)
