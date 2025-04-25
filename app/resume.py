# app/resume.py
import io, requests
from pdfminer.high_level import extract_text
import docx
import os
from supabase import create_client
from dotenv import load_dotenv


load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
supabase     = create_client(SUPABASE_URL, SUPABASE_KEY)

def parse_pdf_bytes(b: bytes) -> str:
    return extract_text(io.BytesIO(b))

def parse_docx_bytes(b: bytes) -> str:
    doc = docx.Document(io.BytesIO(b))
    return "\n".join(p.text for p in doc.paragraphs)

def fetch_and_parse_resume(user_id: str) -> str:
    # 1) Pull resume_url from users table
    resp = (
      supabase
      .table("users")
      .select("resume_url")
      .eq("id", user_id)
      .single()
      .execute()
    )
    url = resp.data.get("resume_url") or ""
    if not url:
        return ""
    # 2) Download the file
    r = requests.get(url)
    r.raise_for_status()
    content = r.content
    # 3) Branch on extension
    if url.lower().endswith(".pdf"):
        return parse_pdf_bytes(content)
    elif url.lower().endswith((".docx", ".doc")):
        return parse_docx_bytes(content)
    else:
        return ""
