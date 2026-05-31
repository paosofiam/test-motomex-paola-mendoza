from fastapi import FastAPI

from app.config import settings


app = FastAPI(title=settings.APP_NAME)


@app.get("/health")
def health():
    return {"status": "ok"}
