from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import assets, agents, agreements, health

app = FastAPI(title="Eqip.ai API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/v1")
app.include_router(assets.router, prefix="/v1")
app.include_router(agents.router, prefix="/v1")
app.include_router(agreements.router, prefix="/v1")
