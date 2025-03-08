import nodriver as uc
import asyncio
from core.database.sqlite import add_company_sent
from core.scrapers.wellfound import get_jobs_wellfound
from core.apollo.apollo import get_apollo_emails
from core.email.client import EmailClient
from typing import Optional
import pandas as pd


class JobProcessor:
    def __init__(self, email_client: Optional[EmailClient] = None):
        self.email_client = email_client

    async def process_companies(self) -> None:
        """Main processing pipeline for company data."""
        try:
            # Get company data
            df = await get_jobs_wellfound()
            if df.empty:
                print("No companies found to process")
                return

            # Enrich with contact information
            df = await get_apollo_emails(df)
            if df.empty:
                print("No contact information found")
                return

            # Process each company
            self._store_company_data(df)

        except Exception as e:
            print(f"Error in main processing: {e}")

    def _store_company_data(self, df: pd.DataFrame) -> None:
        """Store processed company data in database."""
        for _, row in df.iterrows():
            try:
                add_company_sent(
                    contactee_name="John Doe",
                    status="Pending",
                    company_name=row["company_name"],
                    description=row["description"],
                    job_type=row["job_type"],
                    size=row["size"],
                    location=row["location"],
                    website=row["website"],
                    contact_name=row["contact_name"],
                    email=row["email"],
                )
            except Exception as e:
                print(f"Error storing company {row['company_name']}: {e}")


async def main():
    processor = JobProcessor()
    await processor.process_companies()

if __name__ == "__main__":
    uc.loop().run_until_complete(main())
