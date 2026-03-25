import json
import httpx
import asyncio
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

app = FastAPI()

# 1. CORS FIX: allow_credentials MUST be False when origins is "*"
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
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Accept": "application/json"
    }
    async with httpx.AsyncClient(headers=headers, timeout=25.0, follow_redirects=True) as client:
        resp = await client.get(url)
        if resp.status_code != 200 or not resp.text.strip():
            return None
        return resp.text.replace("OmniStudy", "Rahul Maida")

@app.on_event("startup")
async def startup():
    asyncio.create_task(periodic_sync())

async def periodic_sync():
    while True:
        try:
            text = await fetch_source(f"{SOURCE_BASE}/api/AllBatches")
            if text:
                data = json.loads(text)
                cache["batches"] = data.get("data", [])
                print(">>> SYNC: Success")
        except: pass
        await asyncio.sleep(600)

@app.api_route("/", methods=["GET", "HEAD"])
async def root(): return {"status": "online", "owner": "Rahul Maida"}

@app.get("/api/batches")
async def get_batches():
    return cache["batches"]

@app.get("/api/details/{bid}")
async def get_details(bid: str):
    try:
        # Dono checks (BatchId aur batchId) taki error na aaye
        text = await fetch_source(f"{SOURCE_BASE}/api/BatchDetails?BatchId={bid}")
        if not text:
             text = await fetch_source(f"{SOURCE_BASE}/api/BatchDetails?batchId={bid}")
        
        if not text:
            return JSONResponse({"status": "error", "data": {"subjects": []}})
            
        return JSONResponse(content=json.loads(text))
    except Exception as e:
        print(f">>> ERROR: {e}")
        return JSONResponse({"status": "error", "data": {"subjects": []}})

@app.get("/api/content/{bid}/{sid}")
async def get_content(bid: str, sid: str):
    try:
        text = await fetch_source(f"{SOURCE_BASE}/api/BatchContent?BatchId={bid}&SubjectId={sid}")
        if not text:
             text = await fetch_source(f"{SOURCE_BASE}/api/BatchContent?batchId={bid}&subjectId={sid}")
        
        if not text:
            return JSONResponse({"status": "error", "data": []})

        return JSONResponse(content=json.loads(text))
    except Exception as e:
        return JSONResponse({"status": "error", "data": []})
