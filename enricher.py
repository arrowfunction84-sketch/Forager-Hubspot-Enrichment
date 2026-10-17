from config import Settings
from forager_client import ForagerClient

class Enricher:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.forager = ForagerClient(settings)

    async def aclose(self):
        await self.forager.aclose()
