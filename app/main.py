from fastapi import FastAPI
from app.schemas.api import HealthResponse

app = FastAPI(title="SmartData Agent", version="0.1.0")

@app.get("/health", response_model=HealthResponse)
def health():
    return HealthResponse(status="ok", service="smartdata-agent")
