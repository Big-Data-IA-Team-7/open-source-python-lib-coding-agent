from fast_api.routes import user_routes, agent_routes
from fastapi import FastAPI

app = FastAPI()

app.router.include_router(user_routes.router,prefix="/auth", tags=["auth"])
app.router.include_router(agent_routes.router,prefix="/chat", tags=["chat"])