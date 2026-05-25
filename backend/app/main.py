import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.models import *  # noqa: F401, F403
from app.routers import deals, free_games, games, health
from app.routers import admin
from app.routers import alerts
from app.routers import auth
from app.routers import wishlist
from app.scheduler import scheduler, register_jobs

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    register_jobs()
    scheduler.start()
    yield
    scheduler.shutdown()


app = FastAPI(title="GameDeals API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(auth.router)
app.include_router(deals.router)
app.include_router(games.router)
app.include_router(free_games.router)
app.include_router(admin.router)
app.include_router(wishlist.router)
app.include_router(alerts.router)
