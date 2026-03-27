import json, httpx, asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

SOURCE_BASE = "https://omnistudy.netlify.app"
cache = {"batches": []}

async def fetch_from_source(url: str):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": f"{SOURCE_BASE}/",
        "Origin": SOURCE_BASE
    }
    async with httpx.AsyncClient(headers=headers, timeout=20.0, follow_redirects=True) as client:
        try:
            r = await client.get(url)
            if r.status_code == 200:
                # Replace 'OmniStudy' with your name in the text
                return r.text.replace("OmniStudy", "Rahul Maida")
            return None
        except:
            return None

@app.on_event("startup")
async def startup():
    # Initial Sync
    text = await fetch_from_source(f"{SOURCE_BASE}/api/AllBatches")
    if text:
        try:
            data = json.loads(text)
            cache["batches"] = data.get("data", [])
        except: pass

@app.get("/")
def home(): return {"status": "running", "batches": len(cache["batches"])}

@app.get("/api/batches")
async def get_batches(): return cache["batches"]

@app.get("/api/details/{bid}")
async def get_details(bid: str):
    # Try the most logical endpoint
    url = f"{SOURCE_BASE}/api/BatchDetails?BatchId={bid}"
    text = await fetch_from_source(url)
    if not text: return {"data": {"subjects": []}}
    return JSONResponse(content=json.loads(text))

@app.get("/api/content/{bid}/{sid}")
async def get_content(bid: str, sid: str):
    url = f"{SOURCE_BASE}/api/BatchContent?BatchId={bid}&SubjectId={sid}"
    text = await fetch_from_source(url)
    if not text: return {"data": []}
    return JSONResponse(content=json.loads(text))
