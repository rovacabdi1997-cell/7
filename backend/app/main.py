from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from adapters.factory import build_adapter
from api.routes import router
from app.config import API_VERSION, get_settings


def create_app(adapter=None) -> FastAPI:
    settings = get_settings()
    app = FastAPI(title="Turkmen Gips önümçilik gözegçiligi", version=API_VERSION,
                  description="Salt-okalýan API. PLC/SCADA ulgamyna hiç hili ýazgy ýok.")
    app.state.settings = settings
    app.state.adapter = adapter or build_adapter(settings)
    app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins,
                       allow_methods=["GET"], allow_headers=["*"])
    app.include_router(router)
    return app


app = create_app()
