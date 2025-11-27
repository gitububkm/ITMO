from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from src.routers import users_router, news_router, comments_router, auth_router

app = FastAPI(
    title="News API",
    description="CRUD API для управления пользователями, новостями и комментариями с авторизацией",
    version="2.0.0"
)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(news_router)
app.include_router(comments_router)

@app.get("/")
def root():
    return {
        "message": "News API",
        "docs": "/docs",
        "redoc": "/redoc"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

