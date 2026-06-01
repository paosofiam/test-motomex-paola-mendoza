from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session

from app.config import settings
from app.core.error_handlers import register_error_handlers
from app.database import get_db
from app.routers import chats, leads, pre_ordenes, productos
from app.schemas.health import HealthResponse
from app.services import health_service

app = FastAPI(title=settings.APP_NAME)

register_error_handlers(app)

app.include_router(productos.router)
app.include_router(leads.router)
app.include_router(chats.router)
app.include_router(pre_ordenes.router)


@app.get("/health", response_model=HealthResponse)
def health(db: Session = Depends(get_db)):
    return health_service.get_health(db)
