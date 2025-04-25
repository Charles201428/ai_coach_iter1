# app/project.py
import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
supabase     = create_client(SUPABASE_URL, SUPABASE_KEY)

def fetch_current_project(user_id: str) -> str:
    # 1) Get the user's ongoing capstone project title
    cu = (
      supabase
      .table("capstone_users")
      .select("capstone_project")
      .eq("user_id", user_id)
      .is_("date_submitted", None)
      .single()
      .execute()
    ).data or {}
    title = cu.get("capstone_project") or ""
    if not title:
        return ""
    # 2) Lookup its description
    cp = (
      supabase
      .table("capstone_projects")
      .select("project_description")
      .eq("project_title", title)
      .single()
      .execute()
    ).data or {}
    desc = cp.get("project_description") or ""
    return f"{title}: {desc}"
