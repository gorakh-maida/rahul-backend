
from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import httpx
import asyncio
from typing import Dict, Any

app = FastAPI(title="Rahul Maida Study Portal API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

SOURCE_BASE = "https://omnistudy.netlify.app"
cache = {"batches": [], "last_updated": None}

async def sync_data():
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            # Mirror batches
            resp = await client.get(f"{SOURCE_BASE}/api/AllBatches")
            # Replace Branding
            text = resp.text.replace("OmniStudy", "Rahul Maida")
            data = httpx.codes.json_decode(text)
            cache["batches"] = data.get("data", [])
            print("Sync successful.")
        except Exception as e:
            print(f"Sync error: {e}")

@app.on_event("startup")
async def startup():
    asyncio.create_task(periodic_sync())

async def periodic_sync():
    while True:
        await sync_data()
        await asyncio.sleep(300)

@app.get("/api/batches")
async def get_batches():
    return cache["batches"]

@app.get("/api/batch-info")
async def get_batch_info(batchId: str, type: str = "subject"):
    async with httpx.AsyncClient(timeout=30.0) as client:
        url = f"{SOURCE_BASE}/api/BatchInfo?BatchId={batchId}&Type={type}"
        res = await client.get(url)
        text = res.text.replace("OmniStudy", "Rahul Maida")
        return httpx.codes.json_decode(text)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
