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

SOURCE_BASE = "https://omnistudy.netlify.app"
cache = {"batches": []}

async def fetch_source(url: str):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://omnistudy.netlify.app/"
    }
    async with httpx.AsyncClient(headers=headers, timeout=30.0, follow_redirects=True) as client:
        try:
            resp = await client.get(url)
            if resp.status_code == 200:
                print(f">>> API SUCCESS: {url}")
                return resp.text.replace("OmniStudy", "Rahul Maida")
            print(f">>> API ERROR {resp.status_code}: {url}")
            return None
        except Exception as e: 
            print(f">>> FETCH EXCEPTION: {str(e)}")
            return None

async def sync_now():
    print(">>> SYNC STARTING...")
    text = await fetch_source(f"{SOURCE_BASE}/api/AllBatches")
    if text:
        try:
            data = json.loads(text)
            cache["batches"] = data.get("data", [])
            print(f">>> SYNC SUCCESS: {len(cache['batches'])} Batches Cached")
        except: print(">>> JSON PARSE ERROR IN SYNC")

@app.on_event("startup")
async def startup():
    await sync_now()
    asyncio.create_task(periodic_sync())

async def periodic_sync():
    while True:
        await asyncio.sleep(600)
        await sync_now()

@app.get("/")
async def root(): return {"status": "online", "batches": len(cache["batches"])}

@app.get("/api/batches")
async def get_batches(): return cache["batches"]

@app.get("/api/details/{bid}")
async def get_details(bid: str):
    # Try multiple common patterns
    url = f"{SOURCE_BASE}/api/BatchDetails?BatchId={bid}"
    text = await fetch_source(url)
    if not text: return {"data": {"subjects": []}}
    return JSONResponse(content=json.loads(text))

@app.get("/api/content/{bid}/{sid}")
async def get_content(bid: str, sid: str):
    url = f"{SOURCE_BASE}/api/BatchContent?BatchId={bid}&SubjectId={sid}"
    text = await fetch_source(url)
    if not text: return {"data": []}
    return JSONResponse(content=json.loads(text))
