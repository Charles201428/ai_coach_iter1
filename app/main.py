# app/main.py

import os
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Supabase auth helper
from .auth import get_current_user

# Resume & AI model
from .resume import fetch_and_parse_resume
from .models import generate_response

app = FastAPI(title="AI Coach API")

# CORS setup: allow your front-end origin (or use ["*"] for local testing)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # <-- allow everything, for now
    allow_methods=["GET","POST","OPTIONS"],
    allow_headers=["*"],
)




class ChatRequest(BaseModel):
    question: str
    
    
@app.get("/healthz", tags=["infra"])
def health():
    return {"status": "ok"}

@app.get("/resume")
async def get_resume(user=Depends(get_current_user)):
    """
    Fetch & parse the logged-in user's resume (from users.resume_url).
    """
    resume_text = fetch_and_parse_resume(user.id)
    return {"resume_text": resume_text}

@app.post("/chat")
async def chat(req: ChatRequest, user=Depends(get_current_user)):
    """
    Generate an AI coaching response using:
      • Persistent memory
      • Parsed resume
      • Ongoing capstone project
    """
    answer = generate_response(user, req.question)
    return {"answer": answer}
