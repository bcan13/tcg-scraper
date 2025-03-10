import nodriver as uc
from config.config import WELLFOUND_CONFIG, OUR_NAME
from core.database.sqlite import add_company_sent
from core.scrapers.wellfound import get_jobs_wellfound
from core.apollo.apollo import get_apollo_emails
from core.email.client import EmailClient
import pandas as pd
import logging
from utils.generate_random_yopmail import generate_random_yopmail

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create console handler with formatting
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)


class JobProcessor:
    def __init__(self):
        self.email_client = EmailClient.from_env()

    async def process_companies(self) -> None:
        """Main processing pipeline for company data."""
        try:
            logger.info("Starting company processing pipeline")
            # Get company data
            df = await get_jobs_wellfound()
            if df.empty:
                logger.warning("No companies found to process")
                return

            # Enrich with contact information
            df = await get_apollo_emails(df)
            if df.empty:
                logger.warning("No contact information found")
                return

            # Process each company
            self._store_company_data(df)

        except Exception as e:
            logger.error(f"Error in main processing: {str(e)}", exc_info=True)

    def _store_company_data(self, df: pd.DataFrame) -> None:
        """Store processed company data in database."""
        total_companies = len(df)
        successful_sends = 0
        logger.info(
            f"Starting email sending process for {total_companies} companies"
        )

        for index, row in df.iterrows():
            try:
                email = (
                    generate_random_yopmail()
                    if WELLFOUND_CONFIG["is_test_mode"]
                    else row["email"]
                )
                contact_name = row["contact_name"]
                company_name = row["company_name"]

                logger.info(
                    f"Processing company {index + 1}/{total_companies}: "
                    f"{company_name} (Contact: {contact_name}, Email: {email})"
                )

                if self.email_client:
                    # Try to send email first
                    logger.debug(f"Attempting to send email to {email}")
                    sent = self.email_client.send_email(
                        recipient_email=email,
                        recipient_name=contact_name,
                        company_name=company_name,
                    )

                    if sent:
                        logger.info(
                            f"Successfully sent email to {company_name}"
                        )
                        successful_sends += 1

                        # Store in database
                        logger.debug(f"Storing {company_name} in database")
                        stored = add_company_sent(
                            contactee_name=OUR_NAME,
                            status="Pending",
                            company_name=company_name,
                            description=row["description"],
                            job_type=row["job_type"],
                            size=row["size"],
                            location=row["location"],
                            website=row["website"],
                            contact_name=contact_name,
                            email=email,
                        )
                        if stored:
                            logger.debug(
                                f"Successfully stored {company_name} in database"
                            )
                        else:
                            logger.warning(
                                f"Failed to store {company_name} in database"
                            )
                    else:
                        logger.warning(
                            f"Failed to send email to {company_name}"
                        )
                else:
                    logger.error("No email client available")

            except Exception as e:
                logger.error(
                    f"Error processing company {row['company_name']}: {str(e)}",
                    exc_info=True,
                )

        logger.info(
            f"Email sending completed. Success rate: {successful_sends}/{total_companies} "
            f"({(successful_sends / total_companies) * 100:.1f}%)"
        )


async def main():
    logger.info("Starting job processing")
    processor = JobProcessor()
    await processor.process_companies()
    logger.info("Job processing completed")


if __name__ == "__main__":
    uc.loop().run_until_complete(main())
