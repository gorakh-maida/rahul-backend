import json, httpx
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

app = FastAPI()

# 1. Global CORS Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Force Headers Middleware (Browser-Block Prevention)
@app.middleware("http")
async def add_cors_header(request: Request, call_next):
    response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
    return response

TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiI2OWM3N2QzNWFiMDA2MDNiY2JlYWMwZmQiLCJuYW1lIjoiUmFodWwgIiwidGVsZWdyYW1JZCI6bnVsbCwiUGhvdG9VcmwiOiJodHRwczovL2Nkbi1pY29ucy1wbmcuZmxhdGljb24uY29tLzUxMi8zNjA3LzM2MDc0NDQucG5nIiwiaWF0IjoxNzc0Nzc4OTIwLCJleHAiOjE3NzYwNzQ5MjB9.KC4Xg6bszdR2YDaVEL0KjHAQ-pVoYKP6ct3o9F7p-BE"

def get_headers():
    return {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Authorization": f"Bearer {TOKEN}",
        "Cookie": f"accessToken={TOKEN}",
        "Origin": "https://omnistudy.netlify.app",
        "Referer": "https://omnistudy.netlify.app/",
        "Accept": "application/json"
    }

@app.get("/")
async def health():
    return {"status": "Rahul Proxy Online", "token_valid": True}

@app.get("/api/batches")
async def get_batches():
    try:
        async with httpx.AsyncClient(headers=get_headers(), follow_redirects=True, timeout=15.0) as client:
            r = await client.get("https://omnistudy.netlify.app/api/AllBatches")
            return r.json().get("data", [])
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/api/details/{bid}")
async def get_details(bid: str):
    try:
        async with httpx.AsyncClient(headers=get_headers(), follow_redirects=True, timeout=15.0) as client:
            url = f"https://omnistudy.netlify.app/api/BatchInfo?BatchId={bid}&Type=details"
            r = await client.get(url)
            return r.json()
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/api/content/{bid}/{sid}")
async def get_content(bid: str, sid: str):
    try:
        async with httpx.AsyncClient(headers=get_headers(), follow_redirects=True, timeout=15.0) as client:
            url = f"https://omnistudy.netlify.app/api/BatchContents?BatchId={bid}&SubjectId={sid}"
            r = await client.get(url)
            return r.json()
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
