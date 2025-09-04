import uvicorn
from fastapi import FastAPI
from api.api import router
import logging

app = FastAPI(
    title="Healthcare ML Service",
    description="Synthetic Healthcare Data Generation Microservice",
    version="1.0.0"
)

app.include_router(router, prefix="/api/v1")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
