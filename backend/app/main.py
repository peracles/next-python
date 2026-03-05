# backend/app/main.py
from fastapi import FastAPI

app = FastAPI(title="Next-Python API")

@app.get("/")
async def root():
    return {"message": "API is running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}