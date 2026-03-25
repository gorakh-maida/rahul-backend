import json
import httpx
import asyncio
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

app = FastAPI()

# Permissive CORS - Bilkul Open
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

SOURCE_BASE = "https://omnistudy.netlify.app"
cache = {"batches": []}

@app.get("/")
def home(): 
    return {"status": "ok", "msg": "Rahul Maida API is live"}

@app.on_event("startup")
async def startup():
    asyncio.create_task(periodic_sync())

async def periodic_sync():
    while True:
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.get(f"{SOURCE_BASE}/api/AllBatches")
                data = json.loads(resp.text.replace("OmniStudy", "Rahul Maida"))
                cache["batches"] = data.get("data", [])
                print(">>> SYNC: Batches updated successfully")
        except Exception as e:
            print(f">>> SYNC ERROR: {e}")
        await asyncio.sleep(600)

@app.get("/api/batches")
async def get_batches():
    print(">>> REQUEST: /api/batches called")
    return cache["batches"]

@app.get("/api/batch-details")
async def get_details(batchId: str):
    print(f">>> REQUEST: Fetching details for Batch: {batchId}")
    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            # OmniStudy uses 'BatchId' with Capital B and I
            url = f"{SOURCE_BASE}/api/BatchDetails?BatchId={batchId}"
            res = await client.get(url)
            print(f">>> SOURCE STATUS: {res.status_code}")
            return JSONResponse(content=json.loads(res.text.replace("OmniStudy", "Rahul Maida")))
    except Exception as e:
        print(f">>> ERROR in batch-details: {e}")
        return JSONResponse(content={"status":"error", "msg": str(e)}, status_code=200)

@app.get("/api/batch-content")
async def get_content(batchId: str, subjectId: str):
    print(f">>> REQUEST: Fetching Content for Batch: {batchId}, Subject: {subjectId}")
    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            # OmniStudy uses 'BatchId' and 'SubjectId' (Capital S)
            url = f"{SOURCE_BASE}/api/BatchContent?BatchId={batchId}&SubjectId={subjectId}"
            res = await client.get(url)
            return JSONResponse(content=json.loads(res.text.replace("OmniStudy", "Rahul Maida")))
    except Exception as e:
        print(f">>> ERROR in batch-content: {e}")
        return JSONResponse(content={"status":"error", "msg": str(e)}, status_code=200)
