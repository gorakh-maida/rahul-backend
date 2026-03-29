import json, httpx
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# --- YOUR MASTER CONFIG ---
# Maine aapka paste kiya hua token yahan set kar diya hai
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiI2OWM3N2QzNWFiMDA2MDNiY2JlYWMwZmQiLCJuYW1lIjoiUmFodWwgIiwidGVsZWdyYW1JZCI6bnVsbCwiUGhvdG9VcmwiOiJodHRwczovL2Nkbi1pY29ucy1wbmcuZmxhdGljb24uY29tLzUxMi8zNjA3LzM2MDc0NDQucG5nIiwiaWF0IjoxNzc0Nzc4OTIwLCJleHAiOjE3NzYwNzQ5MjB9.KC4Xg6bszdR2YDaVEL0KjHAQ-pVoYKP6ct3o9F7p-BE"
BASE = "https://omnistudy.netlify.app"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Authorization": f"Bearer {TOKEN}", # Token Bypass
    "Cookie": f"accessToken={TOKEN}",    # Cookie Bypass
    "Referer": f"{BASE}/study",
    "Origin": BASE
}

@app.get("/api/batches")
async def get_batches():
    async with httpx.AsyncClient(headers=HEADERS, follow_redirects=True) as client:
        r = await client.get(f"{BASE}/api/AllBatches")
        # Live Sync: Directly returning fresh data from source
        return r.json().get("data", [])

@app.get("/api/details/{bid}")
async def get_details(bid: str):
    async with httpx.AsyncClient(headers=HEADERS, follow_redirects=True) as client:
        # Tried both cases to avoid "Silly Mistakes"
        url = f"{BASE}/api/BatchInfo?BatchId={bid}&Type=details"
        r = await client.get(url)
        data = r.json()
        
        # Data Extraction logic
        subjects = data.get("data", {}).get("subjects", [])
        if not subjects and isinstance(data.get("data"), list):
            subjects = data.get("data")
            
        return {"data": {"subjects": subjects}}

@app.get("/api/content/{bid}/{sid}")
async def get_content(bid: str, sid: str):
    async with httpx.AsyncClient(headers=HEADERS, follow_redirects=True) as client:
        # Using the new Live Content API
        url = f"{BASE}/api/BatchContents?BatchId={bid}&SubjectId={sid}"
        r = await client.get(url)
        return r.json()

@app.get("/")
def home(): return {"status": "Active", "user": "Rahul Maida", "mode": "Bypass-Enabled"}
