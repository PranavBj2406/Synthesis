import uvicorn
from fastapi import FastAPI
from api.api import router

app = FastAPI(
    title="Diabetes Prediction ML Service",
    description="Diabetes and Blood Pressure Prediction Microservice",
    version="2.0.0"
)

# Only include your actual ML API endpoints
app.include_router(router, prefix="/api/v1")

# Optional: a simple health check for container orchestration
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
