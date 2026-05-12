import requests
import json


API_URL = "https://cpaaswa.netcorecloud.net/api/v2/message/nc"

# Netcore API token
AUTH_TOKEN = "YOUR_NETCORE_TOKEN"

# Your WABA source number / sender id
SOURCE = "YOUR_WABA_ID_OR_SOURCE"

# Receiver number with country code
TO_NUMBER = "9198XXXXXXXX"


def send_whatsapp(message):

    headers = {
        "Authorization": f"Bearer {AUTH_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "message": [
            {
                "recipient_whatsapp": TO_NUMBER,
                "recipient_type": "individual",
                "message_type": "text",
                "source": SOURCE,
                "x-apiheader": "custom_data",
                "type_text": [
                    {
                        "text": message
                    }
                ]
            }
        ]
    }

    response = requests.post(
        API_URL,
        headers=headers,
        data=json.dumps(payload)
    )

    print("Status Code:", response.status_code)
    print("Response:", response.text)


# Example
send_whatsapp("Server Down Alert")