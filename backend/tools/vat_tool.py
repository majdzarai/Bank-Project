from zeep import Client
import json
import re
from datetime import datetime

def validate_vat_tool(input_data: str) -> str:
    try:
        # Parse input
        data = json.loads(input_data)
        country_code = data["country_code"].upper()
        vat_number = re.sub(r'[\s\.\-]', '', data["vat_number"])
        
        # Call EU VIES service
        client = Client("https://ec.europa.eu/taxation_customs/vies/checkVatService.wsdl")
        response = client.service.checkVat(countryCode=country_code, vatNumber=vat_number)
        
        # Return result
        result = {
            "valid": bool(response.valid),
            "country_code": response.countryCode,
            "vat_number": response.vatNumber,
            "name": response.name or "Not available",
            "address": response.address or "Not available",
            "timestamp": datetime.now().isoformat()
        }
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        return json.dumps({"error": str(e), "timestamp": datetime.now().isoformat()})