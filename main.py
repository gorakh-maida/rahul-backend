import json, httpx
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

app = FastAPI()

# --- CORS FIX: Purely global allow ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiI2OWM3N2QzNWFiMDA2MDNiY2JlYWMwZmQiLCJuYW1lIjoiUmFodWwgIiwidGVsZWdyYW1JZCI6bnVsbCwiUGhvdG9VcmwiOiJodHRwczovL2Nkbi1pY29ucy1wbmcuZmxhdGljb24uY29tLzUxMi8zNjA3LzM2MDc0NDQucG5nIiwiaWF0IjoxNzc0Nzc4OTIwLCJleHAiOjE3NzYwNzQ5MjB9.KC4Xg6bszdR2YDaVEL0KjHAQ-pVoYKP6ct3o9F7p-BE"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Authorization": f"Bearer {TOKEN}",
    "Cookie": f"accessToken={TOKEN}",
    "Referer": "https://omnistudy.netlify.app/",
    "Origin": "https://omnistudy.netlify.app"
}

@app.get("/api/batches")
async def get_batches():
    try:
        async with httpx.AsyncClient(headers=HEADERS, timeout=20.0, follow_redirects=True) as client:
            r = await client.get("https://omnistudy.netlify.app/api/AllBatches")
            # Agar JSON nahi mila toh error handle karega
            data = r.json()
            return JSONResponse(content=data.get("data", []), headers={"Access-Control-Allow-Origin": "*"})
    except Exception as e:
        return JSONResponse(content={"error": str(e), "msg": "API is down"}, status_code=500)

@app.get("/api/details/{bid}")
async def get_details(bid: str):
    try:
        async with httpx.AsyncClient(headers=HEADERS, timeout=20.0, follow_redirects=True) as client:
            url = f"https://omnistudy.netlify.app/api/BatchInfo?BatchId={bid}&Type=details"
            r = await client.get(url)
            data = r.json()
            return JSONResponse(content=data, headers={"Access-Control-Allow-Origin": "*"})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.get("/api/content/{bid}/{sid}")
async def get_content(bid: str, sid: str):
    try:
        async with httpx.AsyncClient(headers=HEADERS, timeout=20.0, follow_redirects=True) as client:
            url = f"https://omnistudy.netlify.app/api/BatchContents?BatchId={bid}&SubjectId={sid}"
            r = await client.get(url)
            data = r.json()
            return JSONResponse(content=data, headers={"Access-Control-Allow-Origin": "*"})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.get("/")
def health():
    return {"status": "Rahul Backend is Online", "proxy": "OmniStudy Bypassed"}
