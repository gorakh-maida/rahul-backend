import json, httpx, asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

SOURCE_BASE = "https://omnistudy.netlify.app"
cache = {"batches": []}

async def fetch_api(url: str):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0",
        "Referer": "https://omnistudy.netlify.app/",
        "Origin": "https://omnistudy.netlify.app"
    }
    async with httpx.AsyncClient(headers=headers, timeout=15.0) as client:
        try:
            r = await client.get(url)
            if r.status_code == 200:
                print(f"SUCCESS: {url}")
                return r.json()
            else:
                print(f"FAILED ({r.status_code}): {url}")
                return None
        except Exception as e:
            print(f"ERR: {str(e)}")
            return None

@app.on_event("startup")
async def startup():
    # Initial Sync
    r = await fetch_api(f"{SOURCE_BASE}/api/AllBatches")
    if r and r.get("data"): cache["batches"] = r["data"]

@app.get("/api/batches")
async def get_batches(): return cache["batches"]

@app.get("/api/details/{bid}")
async def get_details(bid: str):
    # Try Pattern 1 (BatchId query)
    data = await fetch_api(f"{SOURCE_BASE}/api/BatchDetails?BatchId={bid}")
    
    # Try Pattern 2 (id query) if Pattern 1 is empty
    if not data or not data.get("data") or len(data["data"]["subjects"]) == 0:
        data = await fetch_api(f"{SOURCE_BASE}/api/BatchDetails?id={bid}")
        
    return data

@app.get("/api/content/{bid}/{sid}")
async def get_content(bid: str, sid: str):
    # Try Pattern 1
    data = await fetch_api(f"{SOURCE_BASE}/api/BatchContent?BatchId={bid}&SubjectId={sid}")
    
    # Try Pattern 2 (SubjectId only)
    if not data or not data.get("data") or len(data["data"]) == 0:
        data = await fetch_api(f"{SOURCE_BASE}/api/BatchContent?SubjectId={sid}")
        
    return data
