import json, httpx, asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# We will try both sources
SOURCES = ["https://omni-study.vercel.app", "https://omnistudy.netlify.app"]
cache = {"batches": []}

async def fetch_source(path: str):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Origin": "https://omnistudy.netlify.app",
        "Referer": "https://omnistudy.netlify.app/study"
    }
    
    async with httpx.AsyncClient(headers=headers, timeout=20.0, follow_redirects=True) as client:
        for base in SOURCES:
            try:
                url = f"{base}{path}"
                print(f"DEBUG: Trying {url}")
                resp = await client.get(url)
                if resp.status_code == 200:
                    text = resp.text.replace("OmniStudy", "Rahul Maida")
                    data = json.loads(text)
                    # Agar subjects khali nahi hain, toh hi return karo
                    if "data" in data and (isinstance(data["data"], list) or data["data"].get("subjects")):
                        return data
                    # Backup check for raw list
                    if isinstance(data, list) and len(data) > 0:
                        return {"data": data}
            except Exception as e:
                print(f"DEBUG ERROR: {str(e)}")
                continue
        return None

@app.on_event("startup")
async def sync():
    data = await fetch_source("/api/AllBatches")
    if data:
        cache["batches"] = data.get("data", [])
        print(f"SYNC: {len(cache['batches'])} Batches found")

@app.get("/")
def home(): return {"status": "online", "batches": len(cache["batches"])}

@app.get("/api/batches")
async def get_batches(): return cache["batches"]

@app.get("/api/details/{bid}")
async def get_details(bid: str):
    # Try different query parameters just in case
    data = await fetch_source(f"/api/BatchDetails?BatchId={bid}")
    if not data:
        data = await fetch_source(f"/api/BatchDetails?id={bid}")
    
    if not data:
        return JSONResponse({"status": "error", "data": {"subjects": []}})
    return JSONResponse(data)

@app.get("/api/content/{bid}/{sid}")
async def get_content(bid: str, sid: str):
    data = await fetch_source(f"/api/BatchContent?BatchId={bid}&SubjectId={sid}")
    if not data:
        return JSONResponse({"status": "error", "data": []})
    return JSONResponse(data)
