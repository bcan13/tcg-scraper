import asyncio
from core.scrapers.wellfound import get_jobs_wellfound
from core.apollo.apollo import get_apollo_emails

async def main():
    df = await get_jobs_wellfound()
    await get_apollo_emails(df)

if __name__ == "__main__":
    asyncio.run(main())