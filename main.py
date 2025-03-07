import asyncio
from core.database.sqlite import add_company_sent
from core.scrapers.wellfound import get_jobs_wellfound
from core.apollo.apollo import get_apollo_emails

async def main():
    df = await get_jobs_wellfound()
    df = await get_apollo_emails(df)

    for index, row in df.iterrows():
        add_company_sent(contactee_name = "John Doe", status = "Pending", company_name = row['company_name'], description = row['description'], job_type = row['job_type'], size = row['size'], location = row['location'], website = row['website'], contact_name = row['contact_name'], email = row['email'])

if __name__ == "__main__":
    asyncio.run(main())
