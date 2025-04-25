# app/models.py

import os, requests
from dotenv import load_dotenv
from supabase import create_client

from .resume import fetch_and_parse_resume
from .project import fetch_current_project

load_dotenv()

# HF endpoints & auth
HF_API_TOKEN  = os.getenv("HF_API_TOKEN")
HEADERS       = {"Authorization": f"Bearer {HF_API_TOKEN}"}
COACH_URL     = "https://api-inference.huggingface.co/models/tiiuae/falcon-7b-instruct"
SUM_URL       = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"

# Supabase client (service role)
SUPABASE_URL  = os.getenv("SUPABASE_URL")
SUPABASE_KEY  = os.getenv("SUPABASE_SERVICE_KEY")
supabase      = create_client(SUPABASE_URL, SUPABASE_KEY)

# Config
MEM_LIMIT        = 20
MEM_CHAR_THRESH  = 4000
RES_CHAR_THRESH  = 1500
PROJ_CHAR_THRESH = 2000

def query_hf(url, payload):
    r = requests.post(url, headers=HEADERS, json=payload)
    r.raise_for_status()
    return r.json()

def summarize(text, max_len):
    try:
        out = query_hf(SUM_URL, {
            "inputs": text,
            "parameters": {"max_length": max_len, "min_length":50, "do_sample":False}
        })
        return out[0]["summary_text"].strip()
    except:
        return text[:max_len] + "..."

def fetch_memory(uid):
    resp = (
      supabase
      .table("user_memories")
      .select("memory_text")
      .eq("user_id", uid)
      .order("inserted_at", desc=False)
      .limit(MEM_LIMIT)
      .execute()
    )
    return "\n".join(r["memory_text"] for r in (resp.data or []))

def store_memory(uid, role, txt):
    supabase.table("user_memories").insert({
        "user_id":     uid,
        "memory_text": f"{role}: {txt}"
    }).execute()

def generate_response(user, user_query: str) -> str:
    """
    user: supabase auth user object with .id
    """
    # 1) Memory
    raw_mem = fetch_memory(user.id)
    mem_ctx = summarize(raw_mem, 300) if len(raw_mem)>MEM_CHAR_THRESH else raw_mem

    # 2) Resume
    raw_res = fetch_and_parse_resume(user.id) or ""
    res_ctx = summarize(raw_res, 150) if len(raw_res)>RES_CHAR_THRESH else raw_res

    # 3) Project
    raw_proj = fetch_current_project(user.id) or ""
    proj_ctx= summarize(raw_proj, 200) if len(raw_proj)>PROJ_CHAR_THRESH else raw_proj

    # 4) Build prompt
    parts = []
    if mem_ctx:  parts.append(f"Conversation so far:\n{mem_ctx}")
    if res_ctx:  parts.append(f"User Resume:\n{res_ctx}")
    if proj_ctx: parts.append(f"Ongoing Capstone Project:\n{proj_ctx}")
    parts.append(f"User asks:\n{user_query}\nAssistant:")
    prompt = "\n\n".join(parts)

    # 5) Call HF
    out = query_hf(COACH_URL, {
        "inputs": prompt,
        "parameters": {"max_new_tokens":200, "temperature":0.7}
    })
    gen = out[0].get("generated_text","").strip()
    answer = gen.split("Assistant:",1)[-1].strip() if "Assistant:" in gen else gen

    # 6) Persist
    store_memory(user.id, "user", user_query)
    store_memory(user.id, "assistant", answer)

    return answer
