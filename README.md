# Email Automation 

##Overview
A Python-based email automation tool designed to simply the client aquisition process for TCG. Uses `yagmail` for sending emails with templates for dynamic content generation. Easily customizable and can integrate with external APIs.

## Features
- **Email Sending**: Uses Gmail SMTP for authentication and sending.
- **Template-Based Content**: Predefined templates for email  body and attachments.
- **Personalization**: Inserts dynamic values for a customized experience.


---

## Installation
### Prerequisites
Ensure Python is installed, then install dependencies:
```bash
pip install -r requirements.txt
```
```python
pip install -r requirements.txt
```

## Usage
### Initialize EmailClient
```python
from email_client import EmailClient

mail = EmailClient(our_name='Brian Can')
```

### Sending Email
```python
mail.send_email(
    recipient_email='janedoe@example.com',
    recipient_name='Jane Doe',
    company_name='nSpire AI'
)
```

## Config
### Environmental Variables
Create a .env file with:
```python
EMAIL_USER=your_email@example.com
EMAIL_PASS=your_email_password
```
## Code Overciew

### EmailClient Class
Handles authentication, template reading, content generation, and email sending.

### Methods:

- `read_template(path: str) -> str`: Reads a template file.
- `get_significant_value() -> str`: Selects a random personalization value.
- `create_body(recipient_name, our_name, company_name) -> list`: Generates an email body.
- `create_subject(company_name) -> str:` Generates an email subject.
- `send_email(recipient_email, recipient_name, company_name) -> bool`: Sends an email.

### Templates

Stored in templates/:

- cold_outreach.txt: Email body template.
- significant_values.txt: Personalization values.
- subject.txt: Subject template.
- signature.jpg: Email signature image.
- brochure.pdf: Email attachment.
