import os
import httpx
import logging
from config import Settings
from forager_client import ForagerClient

log = logging.getLogger("enricher")

class Enricher:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.forager = ForagerClient(settings)
        # Railway se direct secret key uthayega
        self.hubspot_token = os.getenv("HUBSPOT_ACCESS_TOKEN")
        self.hs_headers = {
            "Authorization": f"Bearer {self.hubspot_token}",
            "Content-Type": "application/json"
        }

    async def aclose(self):
        await self.forager.aclose()

    async def process_webhook(self, domain: str):
        log.info(f"Processing domain: {domain}")
        
        # 1. Forager se data lena
        data = await self.forager.get_company_data(domain)
        
        async with httpx.AsyncClient() as client:
            # 2. HubSpot mein OpenAI company dhundna
            search_url = "https://api.hubapi.com/crm/v3/objects/companies/search"
            search_payload = {
                "filterGroups": [{"filters": [{"propertyName": "domain", "operator": "EQ", "value": domain}]}]
            }
            search_resp = await client.post(search_url, headers=self.hs_headers, json=search_payload)
            search_data = search_resp.json()
            
            if search_data.get("total", 0) == 0:
                log.error("Company not found in HubSpot")
                return
            
            company_id = search_data["results"][0]["id"]
            
            # 3. HubSpot mein Company ki details Update karna
            update_url = f"https://api.hubapi.com/crm/v3/objects/companies/{company_id}"
            update_payload = {
                "properties": {
                    "description": data["description"],
                    "city": data["city"],
                    "industry": data["industry"]
                }
            }
            await client.patch(update_url, headers=self.hs_headers, json=update_payload)
            
            # 4. HubSpot mein 5 Contacts add karna aur unhe company se jodna
            contact_url = "https://api.hubapi.com/crm/v3/objects/contacts"
            for c in data["contacts"]:
                c_payload = {
                    "properties": {
                        "firstname": c["first_name"],
                        "lastname": c["last_name"],
                        "email": c["email"],
                        "jobtitle": c["job_title"]
                    },
                    "associations": [{"to": {"id": company_id}, "types": [{"associationCategory": "HUBSPOT_DEFINED", "associationTypeId": 1}]}]
                }
                await client.post(contact_url, headers=self.hs_headers, json=c_payload)
            
        log.info("Successfully updated HubSpot!")
