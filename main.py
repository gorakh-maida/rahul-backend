import json
import httpx
import asyncio
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

app = FastAPI()

# 1. Sabse Powerful CORS Settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "HEAD"],
    allow_headers=["*"],
)

SOURCE_BASE = "https://omnistudy.netlify.app"
cache = {"batches": []}

# Function to fetch data with User-Agent (important to avoid blocks)
async def fetch_source(url: str):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    async with httpx.AsyncClient(headers=headers, timeout=20.0, follow_redirects=True) as client:
        resp = await client.get(url)
        # Branding replace logic
        return resp.text.replace("OmniStudy", "Rahul Maida")

@app.on_event("startup")
async def startup():
    asyncio.create_task(periodic_sync())

async def periodic_sync():
    while True:
        try:
            text = await fetch_source(f"{SOURCE_BASE}/api/AllBatches")
            data = json.loads(text)
            cache["batches"] = data.get("data", [])
            print(">>> SYNC STATUS: DATA UPDATED")
        except Exception as e:
            print(f">>> SYNC ERROR: {e}")
        await asyncio.sleep(600)

# Render Health Check Fix (HEAD aur GET dono allow hain)
@app.api_route("/", methods=["GET", "HEAD"])
async def root():
    return {"message": "Server is Running", "owner": "Rahul Maida"}

@app.get("/api/batches")
async def get_batches():
    print(">>> LOG: Fetching all batches")
    return cache["batches"]

@app.get("/api/details/{bid}")
async def get_details(bid: str):
    print(f">>> LOG: Fetching details for {bid}")
    try:
        text = await fetch_source(f"{SOURCE_BASE}/api/BatchDetails?BatchId={bid}")
        return JSONResponse(content=json.loads(text))
    except Exception as e:
        print(f">>> LOG ERROR: {e}")
        return JSONResponse(content={"status":"error", "msg": str(e)}, status_code=200)

@app.get("/api/content/{bid}/{sid}")
async def get_content(bid: str, sid: str):
    print(f">>> LOG: Fetching content for {bid} | {sid}")
    try:
        text = await fetch_source(f"{SOURCE_BASE}/api/BatchContent?BatchId={bid}&SubjectId={sid}")
        return JSONResponse(content=json.loads(text))
    except Exception as e:
        print(f">>> LOG ERROR: {e}")
        return JSONResponse(content={"status":"error", "msg": str(e)}, status_code=200)
