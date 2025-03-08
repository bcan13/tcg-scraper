import nodriver as uc
# Import function to add contacted companies to SQLite database
from core.database.sqlite import add_company_sent
# Import function to scrape job listings from wellfound
from core.scrapers.wellfound import get_jobs_wellfound
# Import function to retrieve email addresses using Apollo.io
from core.apollo.apollo import get_apollo_emails

# Scrape job listings from Wellfound and store in Data Frame #
# and fill DataFrame with email addresses from Apollo.io     #
async def main():
    df = await get_jobs_wellfound()
    df = await get_apollo_emails(df)

    for index, row in df.iterrows():
        # Add each company and contact information to the database #
        # with initial status "Pending"                            #
        add_company_sent(contactee_name = "John Doe", status = "Pending", company_name = row['company_name'], description = row['description'], job_type = row['job_type'], size = row['size'], location = row['location'], website = row['website'], contact_name = row['contact_name'], email = row['email'])

if __name__ == '__main__':
    # Run main async function using nodriver event loop
    uc.loop().run_until_complete(main())
