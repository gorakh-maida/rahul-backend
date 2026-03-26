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
    headers = {"User-Agent": "Mozilla/5.0"}
    async with httpx.AsyncClient(headers=headers, timeout=30.0, follow_redirects=True) as client:
        try:
            resp = await client.get(url)
            if resp.status_code == 200:
                print(f">>> FETCH SUCCESS: {url}")
                return resp.text.replace("OmniStudy", "Rahul Maida")
            return None
        except Exception as e:
            print(f">>> FETCH ERROR: {e}")
            return None

@app.on_event("startup")
async def startup():
    asyncio.create_task(periodic_sync())

async def periodic_sync():
    while True:
        text = await fetch_source(f"{SOURCE_BASE}/api/AllBatches")
        if text:
            data = json.loads(text)
            cache["batches"] = data.get("data", [])
            print(f">>> SYNC SUCCESS: {len(cache['batches'])} Batches")
        await asyncio.sleep(600)

@app.get("/api/batches")
async def get_batches(): return cache["batches"]

@app.get("/api/details/{bid}")
async def get_details(bid: str):
    # Try multiple URL variants to be safe
    text = await fetch_source(f"{SOURCE_BASE}/api/BatchDetails?BatchId={bid}")
    if not text:
        return JSONResponse({"status": "error", "data": {"subjects": []}})
    
    try:
        raw_data = json.loads(text)
        # Check if it's already in the structure we need
        if "data" in raw_data:
            return JSONResponse(raw_data)
        else:
            # If it's a raw list or something else, wrap it
            return JSONResponse({"status": "success", "data": {"subjects": raw_data}})
    except:
        return JSONResponse({"status": "error", "data": {"subjects": []}})

@app.get("/api/content/{bid}/{sid}")
async def get_content(bid: str, sid: str):
    text = await fetch_source(f"{SOURCE_BASE}/api/BatchContent?BatchId={bid}&SubjectId={sid}")
    if not text: return JSONResponse({"status": "error", "data": []})
    
    try:
        raw_data = json.loads(text)
        if "data" in raw_data:
            return JSONResponse(raw_data)
        else:
            return JSONResponse({"status": "success", "data": raw_data})
    except:
        return JSONResponse({"status": "error", "data": []})

@app.api_route("/", methods=["GET", "HEAD"])
async def root(): return {"status": "online"}
