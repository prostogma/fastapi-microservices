from fastapi import FastAPI

from app.api.routers.users import router as user_router


app = FastAPI(title="Users service")

app.include_router(user_router)
