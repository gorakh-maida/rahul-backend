import os
import httpx
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

app = FastAPI()

# Omni Study Style CORS Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Data Storage
cached_batches = []
is_syncing = False

# STUDY RATNA API FETCHING
async def sync_now():
    global cached_batches, is_syncing
    if is_syncing: return
    is_syncing = True
    
    headers = {
        "token": "76ec6a83-a447-49f3-80b3-821ecce89617",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        async with httpx.AsyncClient(verify=False) as client:
            # Fetching from the same source Omni-Study uses
            response = await client.get("https://api.studyrathna.com/api/v1/batches", headers=headers, timeout=30.0)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict) and "data" in data:
                    cached_batches = data["data"]
                else:
                    cached_batches = data if isinstance(data, list) else []
                print(f"✅ Sync Successful: {len(cached_batches)} batches found.")
    except Exception as e:
        print(f"❌ Sync Error: {e}")
    finally:
        is_syncing = False

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(sync_now())

@app.get("/api/batches")
async def get_batches():
    if not cached_batches:
        asyncio.create_task(sync_now())
    return cached_batches

@app.get("/api/details/{bid}")
async def get_details(bid: str):
    headers = {"token": "76ec6a83-a447-49f3-80b3-821ecce89617"}
    async with httpx.AsyncClient(verify=False) as client:
        try:
            url = f"https://api.studyrathna.com/api/v1/batches-details/{bid}"
            res = await client.get(url, headers=headers)
            return res.json()
        except Exception as e:
            return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/api/content/{bid}/{sid}")
async def get_content(bid: str, sid: str):
    headers = {"token": "76ec6a83-a447-49f3-80b3-821ecce89617"}
    async with httpx.AsyncClient(verify=False) as client:
        try:
            url = f"https://api.studyrathna.com/api/v1/batches-contents/{bid}/{sid}"
            res = await client.get(url, headers=headers)
            return res.json()
        except Exception as e:
            return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/")
def home():
    return {"status": "omni-backend-live", "count": len(cached_batches)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
