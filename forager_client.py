import asyncio
import logging
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential
from config import Settings

log = logging.getLogger("forager")

class ForagerClient:
    def __init__(self, settings: Settings):
        self._client = httpx.AsyncClient(
            base_url=settings.forager_base_url,
            headers={"X-API-KEY": settings.forager_api_key, "Content-Type": "application/json"},
            timeout=30.0,
        )
        self._sem = asyncio.Semaphore(4)

    async def aclose(self):
        await self._client.aclose()

    @retry(stop=stop_after_attempt(4), wait=wait_exponential(multiplier=2, min=2, max=30))
    async def _post(self, path: str, payload: dict):
        async with self._sem:
            resp = await self._client.post(path, json=payload)
            if resp.status_code in (401, 403, 404, 422):
                return None
            resp.raise_for_status()
            return resp.json()
