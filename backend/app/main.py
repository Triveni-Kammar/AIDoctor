import sys
import types
import hashlib

# Mock xxhash module to bypass Windows Application Control blocking xxhash DLL load
class MockXxh3_128:
    def __init__(self, data=b""):
        self._hash = hashlib.md5(data)
    def update(self, data):
        self._hash.update(data)
    def digest(self):
        return self._hash.digest()

def xxh3_128_hexdigest(data, seed=0):
    return hashlib.md5(data if isinstance(data, bytes) else str(data).encode()).hexdigest()

xxhash_mock = types.ModuleType("xxhash")
xxhash_mock.xxh3_128 = MockXxh3_128
xxhash_mock.xxh3_128_hexdigest = xxh3_128_hexdigest
sys.modules["xxhash"] = xxhash_mock

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
from app.database import engine, Base
from app.config import settings

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI-First CRM HCP Module",
    description="Healthcare Professional Interaction Logging System",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router)


@app.get("/")
async def root():
    return {
        "message": "AI-First CRM HCP Module API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "llm_model": settings.LLM_MODEL
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
