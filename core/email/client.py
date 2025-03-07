import yagmail
import os
import dotenv
import random
import openai


class EmailClient():

    def __init__(self, our_name):

        self.our_name = our_name

        dotenv.load_dotenv()
        self.email = os.getenv("EMAIL_USER")
        self.password = os.getenv("EMAIL_PASS")

        # self.openai_key = os.getenv("OPENAI_KEY")
        # self.openai_client = openai.OpenAI(api_key=self.openai_key)

        self.body = self.read_template(os.path.join('..', '..', 'templates', 'cold_outreach.txt'))
        self.values = self.read_template(os.path.join('..', '..', 'templates', 'significant_values.txt'))
        #self.prompt = self.read_template(os.path.join('..', '..', 'templates', 'prompt.txt'))
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
            print(f'Failed to read template: {e}')
            return None
        
    # def generate_significant_value(self, company_name: str) -> str:

    #     try:
    #         response = self.openai_client.chat.completions.create(
    #             model = "gpt-3.5-turbo",
    #             messages = [
    #                 {"role": "system", "content": "You are an expert in crafting concise and compelling business value propositions."},
    #                 {"role": "user", "content": self.prompt.format(company_name=company_name)}
    #             ],
    #             max_tokens = 100
    #         )
    #         return response.choices[0].message.content.strip()
    #     except Exception as e:
    #         print(f'Failed to generate significant value: {e}')
    #         return None

    def get_significant_value(self) -> str:

        return random.choice(self.values.split('\n'))


    def create_body(self, recipient_name: str, 
                    our_name: str, 
                    company_name: str, 
                    ) -> list:
        
        try:
            significant_value = self.get_significant_value()

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
        
    def send_email(self,
                   recipient_email: str, 
                   recipient_name: str, 
                   company_name: str,
                   ):
        
        if not self.session:
            print("Failed to send email: No authenticated session.")
            return None


        try:
            body = self.create_body(our_name = self.our_name, 
                                recipient_name = recipient_name, 
                                company_name = company_name)
            subject = self.create_subject(company_name = company_name)

            self.session.send(to=recipient_email, subject=subject, contents=body, attachments=self.attachment)
            print(f'Email sent successfully to {recipient_name} from {company_name} ({recipient_email})!')
            return True
        except Exception as e:
            print(f'Failed to send email: {e}')
            return False
        
# mail = EmailClient(our_name='Brian Can')
# mail.send_email(recipient_email = 'canbrian59@gmail.com', recipient_name = 'Jane Doe', company_name = 'nSpire AI')
# mail.send_email(recipient_email = 'briancan6@gmail.com', recipient_name = 'John Doe', company_name = 'Shield AI')