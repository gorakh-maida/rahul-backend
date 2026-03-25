import os
import httpx
import asyncio
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

app = FastAPI()

# Mirroring Target Site
SOURCE_URL = "https://omni-study-api.vercel.app" # OmniStudy ka backend API

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mirroring Logic: Jo OmniStudy par hai, wahi Rahul Maida par dikhega
@app.get("/api/batches")
async def get_mirror_batches():
    async with httpx.AsyncClient() as client:
        try:
            # Replicating OmniStudy structure
            response = await client.get(f"{SOURCE_URL}/batches", timeout=15.0)
            return response.json()
        except Exception as e:
            return JSONResponse(status_code=500, content={"error": "Source Mirroring Failed"})

@app.get("/api/details/{bid}")
async def get_mirror_details(bid: str):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{SOURCE_URL}/batch-details/{bid}", timeout=15.0)
            return response.json()
        except Exception as e:
            return JSONResponse(status_code=500, content={"error": "Details Mirroring Failed"})

@app.get("/api/content/{bid}/{sid}")
async def get_mirror_content(bid: str, sid: str):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{SOURCE_URL}/content/{bid}/{sid}", timeout=15.0)
            return response.json()
        except Exception as e:
            return JSONResponse(status_code=500, content={"error": "Content Mirroring Failed"})

@app.get("/")
def home():
    return {"message": "Rahul Maida Mirroring System Active", "source": "OmniStudy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
