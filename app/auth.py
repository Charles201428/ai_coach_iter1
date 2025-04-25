# app/auth.py
import os
from supabase import create_client
from fastapi import Header, HTTPException, status

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

async def get_current_user(authorization: str = Header(...)):
    """
    Expects header: Authorization: Bearer <access_token>
    """
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid auth header")
    token = authorization.split(" ", 1)[1]
    # Verify JWT
    user_resp = supabase.auth.get_user(token)
    if user_resp.user is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return user_resp.user  # has .id, .email, etc.
