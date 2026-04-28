"""Analyse et correction de scripts Pine Script."""
from app.services.ai_provider import get_ai_provider


async def debug_script(script: str) -> dict:
    provider = get_ai_provider()
    return await provider.debug_script(script)
