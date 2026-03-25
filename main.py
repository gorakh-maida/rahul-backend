import json
import httpx
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# ISSE EXACTLY AISE HI RAKHEIN - CORS FIX
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Sabhi sites ko allow karega
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SOURCE_BASE = "https://omnistudy.netlify.app"
cache = {"batches": []}

async def sync_data():
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            resp = await client.get(f"{SOURCE_BASE}/api/AllBatches")
            text = resp.text.replace("OmniStudy", "Rahul Maida")
            data = json.loads(text)
            cache["batches"] = data.get("data", [])
            print("Successfully synced with Rahul Maida Server")
        except Exception:
            print("Sync failed")

@app.on_event("startup")
async def startup():
    asyncio.create_task(periodic_sync())

async def periodic_sync():
    while True:
        await sync_data()
        await asyncio.sleep(600)

@app.get("/api/batches")
async def get_batches():
    return cache["batches"]

@app.get("/api/batch-details")
async def get_details(batchId: str):
    async with httpx.AsyncClient(timeout=30.0) as client:
        url = f"{SOURCE_BASE}/api/BatchDetails?BatchId={batchId}"
        res = await client.get(url)
        # Replacing branding in details too
        return json.loads(res.text.replace("OmniStudy", "Rahul Maida"))

@app.get("/api/batch-content")
async def get_content(batchId: str, subjectId: str):
    async with httpx.AsyncClient(timeout=30.0) as client:
        url = f"{SOURCE_BASE}/api/BatchContent?BatchId={batchId}&SubjectId={subjectId}"
        res = await client.get(url)
        return json.loads(res.text.replace("OmniStudy", "Rahul Maida"))

@app.get("/")
def home(): return {"message": "Rahul Maida API is Running"}
