import yagmail
import os
import dotenv

def authenticate():

    dotenv.load_dotenv()

    try:
        sender_email = os.getenv("EMAIL_USER")
        sender_password = os.getenv("EMAIL_PASS")

        yag = yagmail.SMTP(user=sender_email, password=sender_password)

    except Exception as e:
        print("Failed to authenticate the email sender.")
        yag = None

    return yag
