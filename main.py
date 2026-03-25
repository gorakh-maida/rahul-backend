import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import httpx
import asyncio

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
            print("Batches Synced!")
        except Exception as e:
            print(f"Sync error: {e}")

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

# Naya Endpoint: Subjects lane ke liye
@app.get("/api/batch-details")
async def get_details(batchId: str):
    async with httpx.AsyncClient() as client:
        url = f"{SOURCE_BASE}/api/BatchDetails?batchId={batchId}"
        res = await client.get(url)
        return json.loads(res.text.replace("OmniStudy", "Rahul Maida"))

# Naya Endpoint: Videos/PDF lane ke liye
@app.get("/api/batch-content")
async def get_content(batchId: str, subjectId: str):
    async with httpx.AsyncClient() as client:
        url = f"{SOURCE_BASE}/api/BatchContent?batchId={batchId}&subjectId={subjectId}"
        res = await client.get(url)
        return json.loads(res.text.replace("OmniStudy", "Rahul Maida"))

@app.get("/")
def home(): return {"status": "Rahul Maida API is live"}
