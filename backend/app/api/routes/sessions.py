"""
Session history endpoint - powers the sidebar list of past conversations.
"""
from fastapi import APIRouter

from app.db.session import list_sessions

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.get("")
async def get_sessions():
    return list_sessions()