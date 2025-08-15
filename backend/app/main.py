from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.api import api_router
from app.core.config import settings

app = FastAPI(
    title="My First Bank App API",
    description="Parent-managed virtual bank accounts for children",
    version="0.1.0",
)

# CORS middleware - more secure for production
allowed_origins = [
    "http://localhost:3000",  # Local development
    "http://localhost:8080",  # Alternative local port
    "https://your-frontend-domain.com",  # Replace with your actual frontend domain
]

# In development, allow all origins; in production, restrict to specific domains
if settings.DEBUG:
    allowed_origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "My First Bank App API"}


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
