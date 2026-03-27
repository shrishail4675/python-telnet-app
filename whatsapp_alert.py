# Use Twilio API
from twilio.rest import Client

def send_whatsapp(message):
    client = Client("ACCOUNT_SID", "AUTH_TOKEN")

    client.messages.create(
        from_='whatsapp:+14155238886',
        body=message,
        to='whatsapp:+91XXXXXXXXXX'
    )