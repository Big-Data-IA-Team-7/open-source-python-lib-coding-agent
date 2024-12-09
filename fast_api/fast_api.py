from fastapi import FastAPI
from dotenv import load_dotenv

from fast_api.routes import user_routes, agent_routes,github_routes

from logging_module.logging_config import setup_logging

load_dotenv()
logger = setup_logging()

app = FastAPI()

app.router.include_router(user_routes.router,prefix="/auth", tags=["auth"])
app.router.include_router(agent_routes.router,prefix="/chat", tags=["chat"])
app.router.include_router(github_routes.router,prefix="/git", tags=["git"])