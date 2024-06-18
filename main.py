from fastapi import FastAPI, APIRouter
from api.handlers import user_router
import uvicorn

app = FastAPI(title="ProjectPet")

main_api_router = APIRouter()

main_api_router.include_router(user_router, prefix="/users", tags=["users"])
app.include_router(main_api_router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
