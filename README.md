# Project Overview: TCG Scraper
A Python-based email scraping and automation tool designed to simply the client aquisition process for TCG. Intergrates job scraping from listings on wellfound, email extraction from Apollo.io, and personalizes email outreach using GMAIL/STMP client.

## Setup
### Dependencies
Ensure Python is installed, then install dependencies:

```bash
pip install -r requirements.txt
```


**SQLite 3 Editor**

![SQLite Extension Image](https://github.com/user-attachments/assets/a98d8d7b-4481-42e3-87be-30ff4273982e)

To view and edit the database file, install and enable [**this VS Code extension**](https://marketplace.visualstudio.com/items?itemName=mtxr.sqltools-driver-sqlite), and then simply click on the `.db` file.


## Authentication

### Create an App Password with your Google Account

To authenticate your email login, you must create an app password associated with the Google account you are sending emails from. Below are the steps to do so:
1. Enable 2-Step Verification for your Google Account.
2. Visit [**this page**](https://myaccount.google.com/apppasswords).
3. Enter a name for the app password, this can be anything. We called it "MAIL".
4. Copy the 16-letter app password and paste it into the '.env' file detailled below.
   
### Create an .env file in the root folder

Below is a snippet of an example .env file, replace each value with your own.
```python
EMAIL_USER = "johndoe@example.com"
EMAIL_PASS = "abcd efgh ijkl mnop"
CC_EMAIL = "janedoen@example.com" # Optional value if you want to CC another email, otherwise exclude
```

## Configuration

### Edit config.py

The configuration file contains the following values:

- `'OUR NAME' -> str`: The contactee name you wish to use to email contacts
- `'job_titles' -> List[str]`: A list of strings containing each of the job titles off of Wellfound you want to contact 
- `'locations' -> List[str]`: A list of strings containing each of the locations off of Wellfound you want to contact
- `'max_company_size' -> int`: A integer representing the max company size you want to contact
- `'is_test_mode' -> bool`: A boolean indicating whether or not you want to use test mode, which contacts disposable emails for testing

### Test Mode

If you are using test mode, the script will contact dispoable emails from [**Yopmail**], an anonymous and temporary inbox.
This way, you can review the recipient inbox in order to make sure everything is setup and being done correctly. In order to view the recipient inbox:

1. Visit [**Yopmail**](https://yopmail.com/).
2. Enter in the username of the testing recipient email whose inbox you want to see. For instance if I sent an email to abcd@yopmail.com, I would enter in "abcd" to view their inbox.

### Edit Templates

If you want to change the subject or body template in the future, simply locate the `templates/subject.txt` file or the `templates/cold_outreach.txt` file and edit it.

## Extra Details

For more details on this project, including the technology stack and its complete workflow, please visit [**this slideshow**](https://www.canva.com/design/DAGhNtRsvOs/jc7-e9yuTXpoTSUeQp9Rzg/edit?utm_content=DAGhNtRsvOs&utm_campaign=designshare&utm_medium=link2&utm_source=sharebutton).
