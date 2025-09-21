import uvicorn
from api.api import app   # import the FastAPI app already defined in api/api.py

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)