# import uvicorn
# from fastapi import FastAPI, HTTPException, Request, status
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.responses import JSONResponse
# from api.api import router
# import logging
# import traceback
# from config import logger

# app = FastAPI(
#     title="Diabetes Prediction ML Service",
#     description="Diabetes and Blood Pressure Prediction Microservice",
#     version="2.0.0",
#     docs_url="/docs",
#     redoc_url="/redoc"
# )

# # Add CORS middleware for frontend integration
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # Configure based on your frontend URL
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Exception handlers
# @app.exception_handler(HTTPException)
# async def http_exception_handler(request: Request, exc: HTTPException):
#     return JSONResponse(
#         status_code=exc.status_code,
#         content={
#             "status": "error",
#             "message": exc.detail,
#             "details": str(exc)
#         }
#     )

# @app.exception_handler(Exception)
# async def general_exception_handler(request: Request, exc: Exception):
#     logger.error(f"Unhandled exception: {str(exc)}")
#     logger.error(traceback.format_exc())
#     return JSONResponse(
#         status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#         content={
#             "status": "error",
#             "message": "Internal server error",
#             "details": str(exc)
#         }
#     )

# # Include API router
# app.include_router(router, prefix="/api/v1")

# @app.get("/")
# async def root():
#     return {
#         "message": "Diabetes Prediction ML Service API",
#         "status": "running",
#         "version": "2.0.0",
#         "endpoints": {
#             "train": "/api/v1/train",
#             "predict": "/api/v1/predict",
#             "generate": "/api/v1/generate",
#             "validate": "/api/v1/validate",
#             "status": "/api/v1/models/status"
#         }
#     }

# @app.get("/health")
# async def health_check():
#     return {"status": "healthy"}

# if __name__ == "__main__":
#     uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
import uvicorn
import sys
import os
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from api.api import router
import logging
import traceback
from config import logger

# Force UTF-8 encoding for Windows console
if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'

app = FastAPI(
    title="Diabetes Prediction ML Service",
    description="Diabetes and Blood Pressure Prediction Microservice - GAN-Only Mode",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure based on your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "message": exc.detail,
            "details": str(exc)
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unexpected error: {str(exc)}")
    logger.error(traceback.format_exc())
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status": "error",
            "message": "Internal server error",
            "details": str(exc)
        }
    )

# Include API router
app.include_router(router, prefix="/api/v1", tags=["ML Service"])

# Root endpoint
@app.get("/")
async def root():
    return {
        "service": "Diabetes Prediction ML Service",
        "version": "2.0.0",
        "mode": "GAN-Only (GitHub Datasets)",
        "endpoints": {
            "health": "/api/v1/health",
            "train": "/api/v1/train/gan",
            "generate": "/api/v1/generate",
            "status": "/api/v1/models/status",
            "docs": "/docs"
        }
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
