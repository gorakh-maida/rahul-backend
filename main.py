import json, httpx, asyncio
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# CHANGED SOURCE TO VERCEL (As you noticed the redirection)
SOURCE_BASE = "https://omni-study.vercel.app"
cache = {"batches": []}

async def fetch_source(url: str):
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
        "Referer": f"{SOURCE_BASE}/",
        "Accept": "application/json"
    }
    async with httpx.AsyncClient(headers=headers, timeout=20.0, follow_redirects=True) as client:
        try:
            resp = await client.get(url)
            if resp.status_code == 200:
                print(f"DEBUG: Success {url}")
                return resp.text.replace("OmniStudy", "Rahul Maida")
            print(f"DEBUG: Error {resp.status_code} on {url}")
            return None
        except Exception as e:
            print(f"DEBUG: Exception {str(e)}")
            return None

@app.on_event("startup")
async def startup():
    # Initial Sync
    text = await fetch_source(f"{SOURCE_BASE}/api/AllBatches")
    if text:
        try:
            data = json.loads(text)
            cache["batches"] = data.get("data", [])
            print(f"SYNC: {len(cache['batches'])} Batches found")
        except: pass

@app.get("/api/batches")
async def get_batches(): return cache["batches"]

@app.get("/api/details/{bid}")
async def get_details(bid: str):
    # Try multiple URL patterns to ensure data extraction
    urls = [
        f"{SOURCE_BASE}/api/BatchDetails?BatchId={bid}",
        f"https://omnistudy.netlify.app/api/BatchDetails?BatchId={bid}"
    ]
    
    for url in urls:
        text = await fetch_source(url)
        if text:
            try:
                data = json.loads(text)
                if data.get("data") and (data["data"].get("subjects") or len(data["data"]) > 0):
                    return JSONResponse(data)
            except: continue
            
    return {"data": {"subjects": []}}

@app.get("/api/content/{bid}/{sid}")
async def get_content(bid: str, sid: str):
    url = f"{SOURCE_BASE}/api/BatchContent?BatchId={bid}&SubjectId={sid}"
    text = await fetch_source(url)
    if not text: return {"data": []}
    return JSONResponse(json.loads(text))

@app.get("/")
def check(): return {"status": "ok", "batches": len(cache["batches"])}
