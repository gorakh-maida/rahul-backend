import json
import httpx
import asyncio
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

app = FastAPI()

# Sabse pehle CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SOURCE_BASE = "https://omnistudy.netlify.app"
cache = {"batches": []}

@app.on_event("startup")
async def startup():
    asyncio.create_task(periodic_sync())

async def periodic_sync():
    async with httpx.AsyncClient(timeout=30.0) as client:
        while True:
            try:
                resp = await client.get(f"{SOURCE_BASE}/api/AllBatches")
                text = resp.text.replace("OmniStudy", "Rahul Maida")
                data = json.loads(text)
                cache["batches"] = data.get("data", [])
                print("Sync Success")
            except:
                print("Sync Failed")
            await asyncio.sleep(600)

@app.get("/api/batches")
async def get_batches():
    return cache["batches"]

@app.get("/api/batch-details")
async def get_details(batchId: str):
    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            # Dono possibilities check karte hain (BatchId vs batchId)
            url = f"{SOURCE_BASE}/api/BatchDetails?batchId={batchId}"
            res = await client.get(url)
            
            if res.status_code != 200:
                return JSONResponse({"status": "error", "message": "Source returned error"}, status_code=200)
                
            modified_text = res.text.replace("OmniStudy", "Rahul Maida")
            return json.loads(modified_text)
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=200)

@app.get("/api/batch-content")
async def get_content(batchId: str, subjectId: str):
    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            url = f"{SOURCE_BASE}/api/BatchContent?batchId={batchId}&subjectId={subjectId}"
            res = await client.get(url)
            modified_text = res.text.replace("OmniStudy", "Rahul Maida")
            return json.loads(modified_text)
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=200)

@app.get("/")
def home(): return {"status": "ok", "owner": "Rahul Maida"}
