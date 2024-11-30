from fast_api.routes import user_auth
from fastapi import FastAPI

app = FastAPI()

app.router.include_router(user_auth.router,prefix="/auth", tags=["auth"])