# Basic usage
from core.email.client import EmailClient


client = EmailClient.from_env(our_name="Brian Can")

# Send email
client.send_email(
    recipient_email="canbrian59@gmail.com",
    recipient_name="Jane Doe",
    company_name="Example Corp",
)
