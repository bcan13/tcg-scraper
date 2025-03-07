# Email Automation 

A Python-based email automation tool designed to simply the client aquisition process for TCG. Uses `yagmail` to send emails and includes dynamic content generation using templates. Easily customizable and can integrate with external APIs.

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


---

## Usage

### EmailClient Class

Handles email authencation, template reading, content generation, and email sending

```python
from email_client import EmailClient

mail = EmailClient(our_name='Brian Can')
```

### Send Email
```python
mail.send_email(
    recipient_email='janedoe@example.com',
    recipient_name='Jane Doe',
    company_name='nSpire AI'
)
```
---

## Config
### Environmental Variables
Create a .env file with:
```python
EMAIL_USER=your_email@example.com
EMAIL_PASS=your_email_password #use an app password(detailed below)
```
An app password is a 16-digit passcode that gives a less secure app or device permission to access your Google Account(google account help)

**Important**: To create an app password, you need 2-Step Verification on your Google Account.

### Creating and using app passwords

1. Enable 2-Step Verification for your Google Account
2. Go to your Google Account page
3. Select Security
4. Under Signing in to Google, select 2-Step Verification
5. Select App Passwords
6. Choose "Mail" as app and "Other" for the device device
7. Enter a name for the app password
8. Click Generate
9. Copy the App Password and paste it as `EMAIL_PASS`
---

## Code Overciew

### EmailClient Class
Handles authentication, template reading, content generation, and email sending.

### Methods:

- `read_template(path: str) -> str`: Reads a template file.
- `get_significant_value() -> str`: Selects a random personalization value.
- `create_body(recipient_name, our_name, company_name) -> list`: Generates an email body.
- `create_subject(company_name) -> str:` Generates an email subject.
- `send_email(recipient_email, recipient_name, company_name) -> bool`: Sends an email.

## Templates

Stored in templates/:

- `cold_outreach.txt`: Email body template.
- `significant_values.txt`: Personalization values.
- `subject.txt`: Subject template.
- `signature.jpg`: Email signature image.
- `brochure.pdf`: Email attachment.

# Wellfound Job Scraper

Scrapes job listings from Wellfound (AngelList Talent), extracting company details.

### Features
- Job Scraping: Finds listings based on job title and location.
- Filtering: Excludes previously seen companies or those exceeding size limits.
- Storage: Saves data in SQLite and CSV.
- Automation: Uses nodriver for browser automation.

### Usage
```python
import asyncio
from wellfound_scraper import get_jobs_wellfound

asyncio.run(get_jobs_wellfound())
```

# Apollo.io Email Scraper

Extracts verified email addresses and contact names from Apollo.io.

### Features

- Email Extraction: Retrieves verified emails.
- Integration: Works with Wellfound scraper output.
- Automation: Uses nodriver for seamless extraction.

### Usage
```python
import asyncio
import pandas as pd
from apollo_scraper import get_apollo_emails

wellfound_output_df = pd.DataFrame({
    'company_name': ['Example Corp'],
    'website': ['example.com']
})

updated_df = asyncio.run(get_apollo_emails(wellfound_output_df))
print(updated_df)
```
## Dependencies

- `yagmail`: Email sending
- `dotenv`: Environment variable management
- `pandas`: Data processing
- `nodriver`: Browser automation

