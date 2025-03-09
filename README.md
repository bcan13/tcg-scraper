# Project Overview: TCG Scraper
A Python-based email scraping and automation tool designed to simply the client aquisition process for TCG. Intergrates job scraping from listings on wellfound, email extraction from Apollo.io, and personalizes email outreach using gmail STMP.

## Installation
### Prerequisites
Ensure Python is installed, then install dependencies:

```bash
pip install -r requirements.txt
```

### Extensions
[SQLite Database VS Code Extension] (https://marketplace.cursorapi.com/items?itemName=mtxr.sqltools-driver-sqlite)
Install to view and edit database


## Env file

create a .env file containing environmental variables


 
---
# Email Automation 

 Uses `yagmail` to send emails and includes dynamic content generation using templates. Easily customizable and can integrate with external APIs.

## Features
- **Email Sending**: Uses Gmail SMTP for authentication and sending.
- **Template-Based Content**: Predefined templates for email  body and attachments.
- **Personalization**: Inserts dynamic values for a customized experience.


---

## Usage

### EmailClient Class

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

## Code Overciew

### EmailClient Class
Handles authentication, template reading, content generation, and email sending.

### Methods:

- `read_template(path: str) -> str`: Reads a template file.
- - `create_body(recipient_name, our_name, company_name) -> list`: Generates an email body.
- `create_subject(company_name) -> str:` Generates an email subject.
- `send_email(recipient_email, recipient_name, company_name) -> bool`: Sends an email.

## Templates

Stored in templates/:

- `cold_outreach.txt`: Email body template.
- `subject.txt`: Subject template.
- `signature.jpg`: Email signature image.
- `brochure.pdf`: Email attachment.

## Config
### Environmental Variables
Create a .env file with:
```python
EMAIL_USER=your_email@example.com
EMAIL_PASS=your_email_password #use an app password(detailed below)
CC_EMAIL=CC_email@example.com
```
An app password is a 16-digit passcode that gives a less secure app or device permission to access your Google Account(google account help)

**Important**: To create an app password, you need 2-Step Verification on your Google Account.

### Creating and using app passwords

1. Enable 2-Step Verification for your Google Account
2. Go to your Google Account page
3. Select Security
4. Under Signing in to Google, select 2-Step Verification
5. Select App Passwords
6.  Enter a name for the app password
7.  Click Generate
8.  Copy the App Password and paste it as `EMAIL_PASS`
---

# Wellfound Job Scraper

Scrapes job listings from Wellfound, extracting company details for specidic job titles and locations. Collects details such as company name, description, job type, size, location, and website. The script uses the `nodriver` library for browser automation and searches SQLite database to track previously seen companies.


## Features
- **Job Scraping**: Finds listings based on job title and location.
- **Filtering**: Excludes previously seen companies and filters by size limits.
- **Storage**: Saves data in SQLite and CSV.
- **Automation**: Uses nodriver for browser automation.

### Usage
```python
import asyncio
from wellfound_scraper import get_jobs_wellfound

asyncio.run(get_jobs_wellfound())
```

## Code overview
### Functioality 
1. Browser Initialization
- starts browser session using  `nodriver `
2. Config
- Defines job titles, location, and maximum company size for filtering
3. Scraping logic
- Iterates through each job title and location combination.
- Navigates to the Wellfound search page for the specified job title and location.
- Extracts company details (name, description, size, etc.) from the search results.
- Filters out companies that have been seen before or exceed the maximum size limit.
- Visits the company's Wellfound page to extract the company website URL.

4. Data Storage
- Stores the scraped company data in a SQLite database using the add_company_seen function.
- Accumulates all company data in a list and converts it to a Pandas DataFrame.

### Helper Functions
`company_seen_before(company_name: str) -> bool`:
Checks if a company has already been scraped and stored in the database.
`add_company_seen(company_name: str, description: str, job_type: str, size: str, location: str, website: str)`:
Adds a new company to the database



---
# Apollo.io Email Scraper

Extracts verified email addresses and contact names from Apollo.io for companies listed in a dataframe. Uses `nodriver ` for browser automation, search for company dmains, and retrieve verified mail addresses.

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

## Code Overview
`get_apollo_emails` Function: Logs in to Apollo.io, searches for company domains, and extracts email addresses and contact names for each company.

### Parameters
`wellfound_output_df (pd.DataFrame)`: DataFrame containing company data(from the Wellfound scraper). 

### Functionality
1. Browser Initialization:
- Starts a browser session using nodriver.
2. Login to Apollo.io:
- Navigates to the Apollo.io login page and logs in using a pre-configured email.
3. Email Extraction:
- Iterates through each row in the input DataFrame.
- Searches for the company domain on Apollo.io.
- Checks if verified email addresses are available for the company.
- Extracts the contact name and email address if available.
4. Data Update:
- Updates the input DataFrame with the extracted contact name and email address.



