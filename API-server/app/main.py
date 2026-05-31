from fastapi import FastAPI

from app.config import settings
from app.core.error_handlers import register_error_handlers
from app.routers import chats, leads, pre_ordenes, productos

app = FastAPI(title=settings.APP_NAME)

register_error_handlers(app)

app.include_router(productos.router)
app.include_router(leads.router)
app.include_router(chats.router)
app.include_router(pre_ordenes.router)


@app.get("/health")
def health():
    return {"status": "ok"}
