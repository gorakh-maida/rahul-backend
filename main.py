import os
import httpx
import asyncio
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

app = FastAPI()

# ================= ERROR 1: CORS FIX (SABSE IMPORTANT) =================
# Isse Netlify aur Render ke beech ki deewar hat jayegi
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Har origin ko allow kar diya hai
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables to store data
cached_batches = []
is_syncing = False

# ================= DATA SYNC LOGIC (STUDY RATNA) =================
# Yahan wo logic hai jo data fetch karta hai
async def sync_now():
    global cached_batches, is_syncing
    if is_syncing:
        return
    is_syncing = True
    print("Syncing data from Study Ratna...")
    try:
        # NOTE: Yahan main example URL use kar raha hoon jo pichle AI ne diya tha
        # Aap apna asli API URL aur Headers yahan lagayein
        headers = {
            "token": "76ec6a83-a447-49f3-80b3-821ecce89617", # Aapka token agar alag ho toh change kar lena
            "user-agent": "Mozilla/5.0"
        }
        async with httpx.AsyncClient() as client:
            # Batches fetch kar rahe hain
            response = await client.get("https://api.studyrathna.com/api/v1/batches", headers=headers, timeout=20.0)
            if response.status_code == 200:
                data = response.json()
                # Maan lete hain data array mein aa raha hai
                cached_batches = data.get("data", []) if isinstance(data, dict) else data
                print(f"Sync complete! Found {len(cached_batches)} batches.")
            else:
                print(f"Sync failed with status: {response.status_code}")
    except Exception as e:
        print(f"Sync Error: {e}")
    finally:
        is_syncing = False

# Server start hote hi sync shuru kar do
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(sync_now())

# ================= API ROUTES =================

# 1. Get All Batches
@app.get("/api/batches")
async def get_batches():
    # Agar data khali hai, toh background mein sync chalao aur khali list bhej do
    if not cached_batches:
        asyncio.create_task(sync_now())
    return cached_batches

# 2. Get Subject Details (Path Parameter Fixed)
@app.get("/api/details/{bid}")
async def get_details(bid: str):
    headers = {"token": "76ec6a83-a447-49f3-80b3-821ecce89617"} # Same token
    async with httpx.AsyncClient() as client:
        try:
            url = f"https://api.studyrathna.com/api/v1/batches-details/{bid}"
            res = await client.get(url, headers=headers)
            return res.json()
        except Exception as e:
            return JSONResponse(status_code=500, content={"error": str(e)})

# 3. Get Content (Videos/PDFs)
@app.get("/api/content/{bid}/{sid}")
async def get_content(bid: str, sid: str):
    headers = {"token": "76ec6a83-a447-49f3-80b3-821ecce89617"} # Same token
    async with httpx.AsyncClient() as client:
        try:
            url = f"https://api.studyrathna.com/api/v1/batches-contents/{bid}/{sid}"
            res = await client.get(url, headers=headers)
            return res.json()
        except Exception as e:
            return JSONResponse(status_code=500, content={"error": str(e)})

# Home Route
@app.get("/")
def home():
    return {"message": "Rahul Maida Backend is Live!", "syncing": is_syncing}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
