import yagmail
import os
import dotenv

class EmailClient():

    def __init__(self):

        dotenv.load_dotenv()
        self.email = os.getenv("EMAIL_USER")
        self.password = os.getenv("EMAIL_PASS")

        self.body = self.read_template(os.path.join('..', '..', 'templates', 'cold_outreach.txt'))
        self.subject = self.read_template(os.path.join('..', '..', 'templates', 'subject.txt'))
        self.signature = os.path.join('..', '..', 'templates', 'signature.jpg')
        self.attachment = os.path.join('..', '..', 'templates', 'brochure.pdf')

        try:
            self.session = yagmail.SMTP(user=self.email, password=self.password)
            print("Authenticated the email sender.")
        except Exception as e:
            print("Failed to authenticate the email sender.")
            self.session = None


    def read_template(self, path: os.path) -> str:

        try:
            with open(path, 'r') as file:
                return file.read()

        except Exception as e:
            print(f'Failed to read the email template: {e}')
            return None
        

    def create_body(self, recipient_name: str, 
                    our_name: str, 
                    significant_value: str, 
                    company_name: str, 
                    ) -> list:
        
        try:
            body = self.body.format(recipient_name=recipient_name, 
                                    our_name=our_name, 
                                    significant_value=significant_value, 
                                    company_name=company_name)
            signature = yagmail.inline(self.signature)

            return [body, signature]

        except Exception as e:
            print(f'Failed to create body: {e}')
            return None
        
    def create_subject(self, company_name: str) -> str:
    
        try:
            return self.subject.format(company_name=company_name)
        except Exception as e:
            print(f'Failed to create subject: {e}')
            return None
        
    def send_email(self, our_name: str,
                   recipient_email: str, 
                   recipient_name: str, 
                   company_name: str,
                   ):
        
        if not self.session:
            print("Failed to send email: No authenticated session.")
            return None
        
        body = self.create_body(our_name = our_name, 
                                recipient_name = recipient_name, 
                                significant_value = "data-driven insights to enhance decision-making", 
                                company_name = company_name)
        subject = self.create_subject(company_name = company_name)

        try:
            self.session.send(to=recipient_email, subject=subject, contents=body, attachments=self.attachment)
            print(f'Email sent successfully to {recipient_name} from {company_name} ({recipient_email})!')
        except Exception as e:
            print(f'Failed to send email: {e}')
            return None
        
mail = EmailClient()
mail.send_email(our_name = "Brian Can", recipient_email = "canbrian59@gmail.com", recipient_name = "John Doe", company_name = "OpenAI")
mail.send_email(our_name = "Brian Can", recipient_email = "briancan6@gmail.com", recipient_name = "John Doe", company_name = "OpenAI")