import os
import jwt
import redis.asyncio as redis
import httpx
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager

# ---------- Configuration ----------
JWT_SECRET = os.getenv("JWT_SECRET", "change-this-secret")
REDIS_HOST = os.getenv("REDIS_HOST", "redis-service")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", 100))
RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", 60))  # seconds

# Tenant → model endpoint (internal K8s service)
MODEL_ENDPOINTS = {
    "team-alpha": "http://svc-deepseek:8000/v1/completions",
    "team-beta": "http://svc-llama:8000/v1/completions",
    # Add more tenants and models
}

# ---------- Redis connection ----------
redis_client = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global redis_client
    redis_client = await redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
    yield
    await redis_client.close()

app = FastAPI(lifespan=lifespan)
security = HTTPBearer()

# ---------- Auth & Rate limiting ----------
async def verify_token(creds: HTTPAuthorizationCredentials = Depends(security)):
    token = creds.credentials
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        tenant = payload.get("tenant")
        if not tenant:
            raise HTTPException(401, "Missing tenant claim")
        return tenant
    except jwt.InvalidTokenError:
        raise HTTPException(401, "Invalid token")

async def check_rate_limit(tenant: str):
    key = f"rate:{tenant}"
    current = await redis_client.incr(key)
    if current == 1:
        await redis_client.expire(key, RATE_LIMIT_WINDOW)
    if current > RATE_LIMIT_REQUESTS:
        raise HTTPException(429, f"Rate limit exceeded: {RATE_LIMIT_REQUESTS} requests per {RATE_LIMIT_WINDOW}s")

# ---------- API endpoint ----------
@app.post("/v1/completions")
async def completions(
    request: Request,
    tenant: str = Depends(verify_token)
):
    await check_rate_limit(tenant)
    
    body = await request.json()
    model_endpoint = MODEL_ENDPOINTS.get(tenant)
    if not model_endpoint:
        raise HTTPException(400, f"No model assigned to tenant '{tenant}'")
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(model_endpoint, json=body)
            response.raise_for_status()
            return response.json()
        except httpx.TimeoutException:
            raise HTTPException(504, "Model inference timeout")
        except httpx.HTTPStatusError as e:
            raise HTTPException(e.response.status_code, e.response.text)

@app.get("/health")
async def health():
    return {"status": "ok"}
