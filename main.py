import json, httpx, asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

SOURCE_BASE = "https://omnistudy.netlify.app"
cache = {"batches": []}

async def fetch_source(path: str):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Referer": f"{SOURCE_BASE}/study",
        "Origin": SOURCE_BASE
    }
    url = f"{SOURCE_BASE}{path}"
    async with httpx.AsyncClient(headers=headers, timeout=20.0, follow_redirects=True) as client:
        try:
            resp = await client.get(url)
            if resp.status_code == 200:
                print(f"FETCH SUCCESS: {path}")
                return resp.text.replace("OmniStudy", "Rahul Maida")
            return None
        except Exception as e:
            print(f"FETCH ERROR: {str(e)}")
            return None

@app.on_event("startup")
async def sync():
    text = await fetch_source("/api/AllBatches")
    if text:
        data = json.loads(text)
        cache["batches"] = data.get("data", [])
        print(f"SYNCED: {len(cache['batches'])} Batches")

@app.get("/")
def home(): return {"status": "online", "batches": len(cache["batches"])}

@app.get("/api/batches")
async def get_batches(): return cache["batches"]

@app.get("/api/details/{bid}")
async def get_details(bid: str):
    # Trying both common params: BatchId and id
    text = await fetch_source(f"/api/BatchDetails?BatchId={bid}")
    if not text: return {"data": {"subjects": []}}
    return JSONResponse(json.loads(text))

@app.get("/api/content/{bid}/{sid}")
async def get_content(bid: str, sid: str):
    text = await fetch_source(f"/api/BatchContent?BatchId={bid}&SubjectId={sid}")
    if not text: return {"data": []}
    return JSONResponse(json.loads(text))
