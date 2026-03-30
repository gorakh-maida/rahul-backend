import json, httpx
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

app = FastAPI()

# --- HARDCORE CORS BYPASS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Aapka Master Token (2026 tak valid)
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiI2OWM3N2QzNWFiMDA2MDNiY2JlYWMwZmQiLCJuYW1lIjoiUmFodWwgIiwidGVsZWdyYW1JZCI6bnVsbCwiUGhvdG9VcmwiOiJodHRwczovL2Nkbi1pY29ucy1wbmcuZmxhdGljb24uY29tLzUxMi8zNjA3LzM2MDc0NDQucG5nIiwiaWF0IjoxNzc0Nzc4OTIwLCJleHAiOjE3NzYwNzQ5MjB9.KC4Xg6bszdR2YDaVEL0KjHAQ-pVoYKP6ct3o9F7p-BE"

# Common Headers for all requests
def get_headers():
    return {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Authorization": f"Bearer {TOKEN}",
        "Cookie": f"accessToken={TOKEN}",
        "Referer": "https://omnistudy.netlify.app/",
        "Origin": "https://omnistudy.netlify.app",
        "Accept": "application/json"
    }

@app.get("/api/batches")
async def get_batches():
    try:
        async with httpx.AsyncClient(headers=get_headers(), follow_redirects=True, timeout=30.0) as client:
            r = await client.get("https://omnistudy.netlify.app/api/AllBatches")
            resp = r.json()
            # CORS Force Headers
            return JSONResponse(
                content=resp.get("data", []), 
                headers={"Access-Control-Allow-Origin": "*"}
            )
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.get("/api/details/{bid}")
async def get_details(bid: str):
    try:
        async with httpx.AsyncClient(headers=get_headers(), follow_redirects=True, timeout=30.0) as client:
            # Silly mistake prevention: Mapping Both BatchId Case
            url = f"https://omnistudy.netlify.app/api/BatchInfo?BatchId={bid}&Type=details"
            r = await client.get(url)
            return JSONResponse(content=r.json(), headers={"Access-Control-Allow-Origin": "*"})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.get("/api/content/{bid}/{sid}")
async def get_content(bid: str, sid: str):
    try:
        async with httpx.AsyncClient(headers=get_headers(), follow_redirects=True, timeout=30.0) as client:
            url = f"https://omnistudy.netlify.app/api/BatchContents?BatchId={bid}&SubjectId={sid}"
            r = await client.get(url)
            return JSONResponse(content=r.json(), headers={"Access-Control-Allow-Origin": "*"})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.get("/")
def health():
    return {"status": "Rahul Maida Portal Engine - Online", "version": "2.0.1"}
