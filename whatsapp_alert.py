import requests
import config


def send_whatsapp(template_name, attributes):

    headers = {
        "Authorization": f"Bearer {config.API_KEY}",
        "Content-Type": "application/json"
    }

    results = []

    for number in config.TO_NUMBERS:

        print("Sending to:", number)

        payload = {
            "message": [
                {
                    "recipient_whatsapp": number,
                    "recipient_type": "individual",
                    "message_type": "template",
                    "type_template": [
                        {
                            "name": template_name,
                            "attributes": attributes,
                            "language": {
                                "locale": "en",
                                "policy": "deterministic"
                            }
                        }
                    ]
                }
            ]
        }

        print(payload)

        try:
            response = requests.post(
                config.URL,
                headers=headers,
                json=payload,
                timeout=30
            )

            print(f"{number} : {response.status_code}")
            print(response.text)

            results.append(response.json())

        except requests.exceptions.RequestException as e:
            print(f"{number} : Error: {e}")

    return results

# if __name__ == '__main__':
#     send_whatsapp(template_name="connectivity_notification_inav",
#                   attributes=["success", "testing", "success"])
