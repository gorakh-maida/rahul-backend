import json
import httpx
import asyncio
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

app = FastAPI()

# 1. Standard CORS Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Manual CORS Header (Extra Protection)
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    if request.method == "OPTIONS":
        return Response(content="OK", status_code=200, headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "*",
            "Access-Control-Allow-Headers": "*"
        })
    response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response

SOURCE_BASE = "https://omnistudy.netlify.app"
cache = {"batches": []}

async def sync_data():
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            resp = await client.get(f"{SOURCE_BASE}/api/AllBatches")
            text = resp.text.replace("OmniStudy", "Rahul Maida")
            data = json.loads(text)
            cache["batches"] = data.get("data", [])
            print(">>> SYNC: Success")
        except:
            print(">>> SYNC: Failed")

@app.on_event("startup")
async def startup():
    asyncio.create_task(periodic_sync())

async def periodic_sync():
    while True:
        await sync_data()
        await asyncio.sleep(600)

@app.get("/")
def home(): return {"status": "ok", "owner": "Rahul Maida"}

@app.get("/api/batches")
async def get_batches():
    return cache["batches"]

# Endpoints modified to PATH style for better CORS handling
@app.get("/api/details/{id}")
async def get_details(id: str):
    async with httpx.AsyncClient(timeout=20.0) as client:
        url = f"{SOURCE_BASE}/api/BatchDetails?BatchId={id}"
        res = await client.get(url)
        processed = res.text.replace("OmniStudy", "Rahul Maida")
        return JSONResponse(content=json.loads(processed))

@app.get("/api/content/{bid}/{sid}")
async def get_content(bid: str, sid: str):
    async with httpx.AsyncClient(timeout=20.0) as client:
        url = f"{SOURCE_BASE}/api/BatchContent?BatchId={bid}&SubjectId={sid}"
        res = await client.get(url)
        processed = res.text.replace("OmniStudy", "Rahul Maida")
        return JSONResponse(content=json.loads(processed))
