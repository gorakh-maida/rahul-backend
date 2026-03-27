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
async def proxy_engine(path: str, request: Request):
    # Default landing page
    current_path = path if path else "MissionJeet/"
    
    # Query parameters parse karein
    params = str(request.query_params)
    target_url = f"{TARGET_BASE}/{current_path}"
    if params:
        target_url += f"?{params}"

    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get(target_url, headers=headers, timeout=20)
        
        # Static files (Images/JS/CSS) ko bina chhede bhej do
        if "text/html" not in resp.headers.get("Content-Type", ""):
            return Response(content=resp.content, media_type=resp.headers.get("Content-Type"))

        html = resp.text

        # 1. FIX LINKS: Redirection rokne ke liye
        # Isse har folder click karne par URL aapki netlify site hi rahegi
        def fix_href(match):
            link = match.group(1)
            if link.startswith(("http", "tel", "mailto", "#", "javascript")):
                return match.group(0)
            return f'href="/?path=MissionJeet/{link.lstrip("/")}"'

        html = re.sub(r'href="([^"]+)"', fix_href, html)

        # 2. BRANDING: Name replacement
        html = html.replace("RolexCoderZ", "Rahul Maida Study")
        html = html.replace("RolexCoderz", "Rahul Maida Study")
        html = html.replace("Rolex", "Rahul Maida")
        
        # 3. ASSETS FIX: <base> tag inject karna taaki JS/CSS load ho sake
        base_tag = f'<base href="{TARGET_BASE}/MissionJeet/">'
        html = html.replace("<head>", f"<head>{base_tag}")

        return HTMLResponse(content=html)

    except Exception as e:
        return HTMLResponse(content=f"<h3>Error Connecting to Server: {str(e)}</h3>")
