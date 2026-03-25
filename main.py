import json, httpx, asyncio
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

SOURCE_BASE = "https://omnistudy.netlify.app"
cache = {"batches": []}

async def fetch_source(url: str):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }
    async with httpx.AsyncClient(headers=headers, timeout=25.0, follow_redirects=True) as client:
        try:
            resp = await client.get(url)
            if resp.status_code == 200:
                return resp.text.replace("OmniStudy", "Rahul Maida")
            return None
        except: return None

async def sync_now():
    print(">>> SYNC: Fetching data from source...")
    text = await fetch_source(f"{SOURCE_BASE}/api/AllBatches")
    if text:
        data = json.loads(text)
        cache["batches"] = data.get("data", [])
        print(f">>> SYNC: Success! Found {len(cache['batches'])} batches")
    else:
        print(">>> SYNC: Failed to fetch")

@app.on_event("startup")
async def startup():
    # Force immediate sync on start
    await sync_now()
    # Then start background refresh
    asyncio.create_task(periodic_sync())

async def periodic_sync():
    while True:
        await asyncio.sleep(600)
        await sync_now()

@app.api_route("/", methods=["GET", "HEAD"])
async def root(): return {"status": "online", "cache_size": len(cache["batches"])}

@app.get("/api/batches")
async def get_batches(): return cache["batches"]

@app.get("/api/details/{bid}")
async def get_details(bid: str):
    text = await fetch_source(f"{SOURCE_BASE}/api/BatchDetails?BatchId={bid}")
    if not text: return JSONResponse({"status": "error", "data": {"subjects": []}})
    return JSONResponse(content=json.loads(text))

@app.get("/api/content/{bid}/{sid}")
async def get_content(bid: str, sid: str):
    text = await fetch_source(f"{SOURCE_BASE}/api/BatchContent?BatchId={bid}&SubjectId={sid}")
    if not text: return JSONResponse({"status": "error", "data": []})
    return JSONResponse(content=json.loads(text))
