from auth import authenticate
import yagmail
import os

def read_template(path):

    try:
        with open(path, 'r') as file:
            template = file.read()

    except Exception as e:
        print(f"Failed to read the email template: {e}")
        template = None

    return template

def create_body(recipient_name, our_name, significant_value, company_name, body_template_path = os.path.join('..', 'templates', 'cold_outreach.txt')):

    body = read_template(body_template_path)
    body = body.format(recipient_name=recipient_name, 
                                our_name=our_name, 
                                significant_value=significant_value, 
                                company_name=company_name)
    
    signature_path = os.path.join('..', 'templates', 'signature.jpg')
    signature = yagmail.inline(signature_path)

    return [body, signature]

def create_subject(company_name, subject_template_path = os.path.join('..', 'templates', 'subject.txt')):

    subject = read_template(subject_template_path)
    subject = subject.format(company_name=company_name)
    
    return subject

def send_email(recipient_email, recipient_name, subject, body, attachment_path = os.path.join('..', 'templates', 'brochure.pdf')):

    yag = authenticate()

    if yag:

        try:
            yag.send(to=recipient_email, subject=subject, contents=body, attachments=attachment_path)
            print(f"Email sent successfully to {recipient_name} ({recipient_email})!")

        except Exception as e:
            print(f"Failed to send email: {e}")

body = create_body("Brian Can", "aathi", "data-driven insights to enhance decision-making", "tcg")
subject = create_subject("Company Name")
send_email("aathijmuthu@gmail.com", "Brian Can", subject, body)