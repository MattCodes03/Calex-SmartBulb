import os
import json

from dotenv import load_dotenv
from tuya_connector import TuyaOpenAPI


load_dotenv()


class CalexBulb:
    """Control a CALEX A60 RGB+CCT bulb through Tuya Cloud."""

    def __init__(self, device_id=None):
        self.device_id = device_id or os.getenv("TUYA_DEVICE_ID")

        if not self.device_id:
            raise RuntimeError("TUYA_DEVICE_ID is missing from .env")

        access_id = os.getenv("TUYA_ACCESS_ID")
        access_secret = os.getenv("TUYA_ACCESS_SECRET")
        endpoint = os.getenv("TUYA_ENDPOINT")

        if not all([access_id, access_secret, endpoint]):
            raise RuntimeError("Missing Tuya configuration in .env")

        self.api = TuyaOpenAPI(
            endpoint,
            access_id,
            access_secret,
        )

        response = self.api.connect()

        if not response.get("success"):
            raise RuntimeError(f"Tuya connection failed: {response}")

    def _command(self, code, value):
        """Send a single command to the bulb."""

        response = self.api.post(
            f"/v1.0/iot-03/devices/{self.device_id}/commands",
            {
                "commands": [
                    {
                        "code": code,
                        "value": value,
                    }
                ]
            },
        )

        if not response.get("success"):
            raise RuntimeError(f"Command failed: {response}")

        return response

    def on(self):
        """Turn the bulb on."""
        return self._command("switch_led", True)

    def off(self):
        """Turn the bulb off."""
        return self._command("switch_led", False)

    def is_on(self):
        """Return True if the bulb is currently on."""

        status = self.status()

        for item in status:
            if item["code"] == "switch_led":
                return item["value"]

        return None

    def brightness(self, percent):
        """
        Set brightness from 0-100%.

        Tuya uses a range of 10-1000 for this bulb.
        """

        percent = max(0, min(100, percent))

        # 0% means off
        if percent == 0:
            return self.off()

        value = int(10 + (percent / 100) * 990)

        return self._command(
            "bright_value_v2",
            value,
        )

    def rgb(self, red, green, blue):
        """
        Set RGB colour.

        r, g, b are 0-255.
        """

        red = max(0, min(255, red))
        green = max(0, min(255, green))
        blue = max(0, min(255, blue))

        # Tuya colour_data_v2 uses HSV.
        h, s, v = self._rgb_to_hsv(red, green, blue)

        colour_data = {
            "h": h,
            "s": s,
            "v": v,
        }

        self._command(
            "work_mode",
            "colour",
        )

        return self._command(
            "colour_data_v2",
            json.dumps(colour_data),
        )

    def temperature(self, percent):
        """
        Set white colour temperature.

        0% = warmest
        100% = coolest
        """

        percent = max(0, min(100, percent))

        # Your bulb reports temp_value_v2.
        # Tuya commonly uses 0-1000 for this datapoint.
        value = int(percent * 10)

        self._command(
            "work_mode",
            "white",
        )

        return self._command(
            "temp_value_v2",
            value,
        )

    def status(self):
        """Return the complete current bulb status."""

        response = self.api.get(
            f"/v1.0/iot-03/devices/{self.device_id}/status"
        )

        if not response.get("success"):
            raise RuntimeError(f"Status request failed: {response}")

        return response["result"]

    def _rgb_to_hsv(self, r, g, b):
        """Convert RGB 0-255 to Tuya's HSV representation."""

        r /= 255
        g /= 255
        b /= 255

        maximum = max(r, g, b)
        minimum = min(r, g, b)

        difference = maximum - minimum

        # Hue
        if difference == 0:
            h = 0
        elif maximum == r:
            h = (60 * ((g - b) / difference)) % 360
        elif maximum == g:
            h = 60 * ((b - r) / difference) + 120
        else:
            h = 60 * ((r - g) / difference) + 240

        # Saturation
        if maximum == 0:
            s = 0
        else:
            s = difference / maximum

        # Value
        v = maximum

        # Tuya v2 colour values use:
        # h: 0-360
        # s: 0-1000
        # v: 0-1000

        return (
            int(h),
            int(s * 1000),
            int(v * 1000),
        )


if __name__ == "__main__":

    bulb = CalexBulb()

    print("Connected to CALEX bulb")
    print("On:", bulb.is_on())

    print("\nStatus:")
    print(json.dumps(bulb.status(), indent=2))
