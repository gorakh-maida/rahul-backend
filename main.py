from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import requests
import re

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

TARGET_BASE = "https://rolexcoderz.in"

@app.get("/{path:path}")
async def master_proxy(path: str, request: Request):
    if not path or path == "/":
        path = "MissionJeet/"
    
    query_params = str(request.query_params)
    target_url = f"{TARGET_BASE}/{path}"
    if query_params:
        target_url += f"?{query_params}"

    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Referer": TARGET_BASE
        }
        
        resp = requests.get(target_url, headers=headers, timeout=30)
        content_type = resp.headers.get("Content-Type", "")

        # Sirf HTML content ko filter karna hai
        if "text/html" not in content_type:
            return Response(content=resp.content, media_type=content_type)

        html = resp.text

        # 1. FIX ASSETS: Script, CSS, Images ko absolute banana taaki "Not defined" error na aaye
        # Ye saare relative links ko https://rolexcoderz.in/... se replace karega
        html = re.sub(r'(src|href)=["\'](?!\/|http|https|#|javascript|tel|mailto)([^"\']+)["\']', 
                      rf'\1="{TARGET_BASE}/MissionJeet/\2"', html)
        html = re.sub(r'(src|href)=["\']\/([^"\']+)["\']', 
                      rf'\1="{TARGET_BASE}/\2"', html)

        # 2. BRANDING: Name Change
        html = html.replace("RolexCoderZ", "Rahul Maida Study")
        html = html.replace("Rolex", "Rahul Maida")
        html = html.replace("Rolex Coderz", "Rahul Maida Study")
        html = html.replace("RC", "RM")

        # 3. INTERCEPT CLICKS: Course folders ke links ko hamare query path mein badalna
        # Taaki website hamare hi domain par rahe
        def link_intercept(match):
            original = match.group(2)
            if "content/index.php" in original:
                return f'href="/?path=MissionJeet/{original}"'
            return match.group(0)

        html = re.sub(r'href=(["\'])([^"\']+)\1', link_intercept, html)

        return HTMLResponse(content=html)

    except Exception as e:
        return HTMLResponse(content=f"<h3>Syncing... Please Refresh. Error: {str(e)}</h3>")

@app.get("/")
def check():
    return {"status": "Rahul Maida API Live"}
