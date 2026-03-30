from fastapi import FastAPI, UploadFile, File, HTTPError
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import os
import io
from PyPDF2 import PdfReader
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
KILO_API_URL = "https://api.kilo.ai/api/gateway/chat/completions"
DEFAULT_MODEL = "kilo-auto/free"

def get_api_key():
    return os.getenv("VITE_KILO_API_KEY") or os.getenv("KILO_API_KEY")

class ChatRequest(BaseModel):
    messages: list
    model: str = DEFAULT_MODEL
    temperature: float = 0.7

@app.get("/api/health")
def health_check():
    return {"status": "ok", "message": "Vercel Python backend is alive"}

@app.post("/api/parse-pdf")
async def parse_pdf(file: UploadFile = File(...)):
    try:
        content = await file.read()
        pdf_file = io.BytesIO(content)
        reader = PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return {"text": text}
    except Exception as e:
        raise HTTPError(status_code=500, detail=str(e))

@app.post("/api/ai-chat")
async def ai_chat(req: ChatRequest):
    api_key = get_api_key()
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    
    try:
        payload = {
            "model": req.model,
            "messages": req.messages,
            "temperature": req.temperature,
            "max_tokens": 1000
        }
        
        response = requests.post(
            KILO_API_URL, 
            headers=headers, 
            json=payload,
            timeout=30
        )
        
        if response.status_code != 200:
            return {"error": f"Gateway Error {response.status_code}", "detail": response.text}
            
        return response.json()
    except Exception as e:
        return {"error": str(e)}

# Vercel expects a module-level 'app' object
# We rename it locally to avoid confusion, but Vercel needs it as the handler
handler = app
