import requests
import config


def send_whatsapp(message_text):
    message_text = "All iNav are updated in Database via application testing"
    headers = {
        "Authorization": f"Bearer {config.API_KEY}",
        "Content-Type": "application/json"
    }

    messages = [
        {
            "recipient_whatsapp": number,
            "recipient_type": "individual",
            "message_type": "template",
            "type_template": [
                {
                    "name": "database_price_check_success_inav",
                    "attributes": [
                        message_text,
                        "https://netcorecloud.com/"
                    ],
                    "language": {
                        "locale": "en",
                        "policy": "deterministic"
                    }
                }
            ]
        }
        for number in config.TO_NUMBERS
    ]

    payload = {
        "message": messages
    }

    try:

        response = requests.post(
            config.URL,
            headers=headers,
            json=payload,
            timeout=30
        )

        print("Status Code:", response.status_code)
        print("Response:", response.text)

        return response.json()

    except requests.exceptions.RequestException as e:

        print("Error:", str(e))
        return None
