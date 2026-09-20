import os
import json

from dotenv import load_dotenv
from tuya_connector import TuyaOpenAPI

load_dotenv()

openapi = TuyaOpenAPI(
    os.getenv("TUYA_ENDPOINT"),
    os.getenv("TUYA_ACCESS_ID"),
    os.getenv("TUYA_ACCESS_SECRET")
)

response = openapi.connect()

print("Connected:", response.get("success"))

# Get devices linked to the Tuya project
response = openapi.get("/v1.0/iot-01/associated-users/devices")

print(json.dumps(response, indent=2))
