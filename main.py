import json
import httpx
import asyncio
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

app = FastAPI()

# Standard CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom Middleware (Double Protection for CORS)
@app.middleware("http")
async def custom_cors_middleware(request: Request, call_next):
    if request.method == "OPTIONS":
        return JSONResponse(status_code=200, content="OK", headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "*",
            "Access-Control-Allow-Headers": "*"
        })
    response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response

SOURCE_BASE = "https://omnistudy.netlify.app"
cache = {"batches": []}

@app.on_event("startup")
async def startup():
    asyncio.create_task(periodic_sync())

async def periodic_sync():
    async with httpx.AsyncClient(timeout=30.0) as client:
        while True:
            try:
                resp = await client.get(f"{SOURCE_BASE}/api/AllBatches")
                data = json.loads(resp.text.replace("OmniStudy", "Rahul Maida"))
                cache["batches"] = data.get("data", [])
            except: pass
            await asyncio.sleep(600)

@app.get("/api/batches")
async def get_batches():
    return cache["batches"]

# Naya Structure: Query ki jagah Path use karenge
@app.get("/api/details/{id}")
async def get_details(id: str):
    async with httpx.AsyncClient(timeout=20.0) as client:
        url = f"{SOURCE_BASE}/api/BatchDetails?BatchId={id}"
        res = await client.get(url)
        return JSONResponse(content=json.loads(res.text.replace("OmniStudy", "Rahul Maida")))

@app.get("/api/content/{bid}/{sid}")
async def get_content(bid: str, sid: str):
    async with httpx.AsyncClient(timeout=20.0) as client:
        url = f"{SOURCE_BASE}/api/BatchContent?BatchId={bid}&SubjectId={sid}"
        res = await client.get(url)
        return JSONResponse(content=json.loads(res.text.replace("OmniStudy", "Rahul Maida")))

@app.get("/")
def home(): return {"status": "running"}
