# backend/app/main.py
from fastapi import FastAPI

app = FastAPI(title="Next-Python API")

@app.get("/")
async def root():
    return {"message": "API is running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/test")
async def test_hot_reload():
    return {"hot_reload": "works"}