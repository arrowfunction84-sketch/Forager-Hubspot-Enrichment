import logging
from fastapi import FastAPI, Request
from config import get_settings
from enricher import Enricher

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("main")

app = FastAPI(title="Forager HubSpot")

@app.get("/")
async def root():
    return {"status": "online"}

@app.post("/webhook/hubspot")
async def hubspot_webhook(request: Request):
    try:
        body = await request.json()
        log.info(f"Webhook received: {body}")
        
        # Postman se bheja gaya domain nikalna
        domain = body.get("company_domain")
        if not domain:
            return {"status": "success", "message": "Ignored: No domain"}

        settings = get_settings()
        enricher = Enricher(settings)
        
        # Asli kaam yahan trigger hoga
        await enricher.process_webhook(domain)
        
        await enricher.aclose()
        return {"status": "success", "message": "Data enriched in HubSpot!"}
    except Exception as e:
        log.error(f"Error: {e}")
        return {"status": "error", "message": str(e)}
