import nodriver as uc
import pandas as pd
from typing import Optional
import logging

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


class ApolloClient:
    def __init__(self):
        self.browser = None
        self.page = None

    async def initialize(self) -> None:
        """Initialize the browser and login to Apollo."""
        logger.info("Initializing Apollo client")
        self.browser = await uc.start(no_sandbox=True)
        self.page = await self.browser.get("https://app.apollo.io/#/login")
        await self._login()

    async def _login(self) -> None:
        """Handle Apollo login process."""
        logger.info("Attempting to log in to Apollo")
        try:
            await self.page.wait_for(
                selector='input[name="email"]', timeout=float("inf")
            )
            login_email = await self.page.select(
                'button[class="zp-button zp_GGHzP zp_Kbe5T zp_PLp2D zp_rduLJ zp_g5xYz"]'
            )
            await login_email.click()
            await self.page.wait_for(text="Quick search", timeout=float("inf"))
            logger.info("Successfully logged in to Apollo")
        except Exception as e:
            logger.error(
                f"Failed to log in to Apollo: {str(e)}", exc_info=True
            )
            raise

    async def _extract_contact_info(self) -> Optional[tuple[str, str]]:
        """Extract name and email from the first person in the search results."""
        try:
            # Get the first person's container
            first_person = await self.page.query_selector_all("div.zp_hWv1I")
            first_person = first_person[1]
            if not first_person:
                logger.warning("No person found in search results")
                return None, None

            # Extract name from first person
            name_elem = await first_person.query_selector(
                "a.zp_p2Xqs.zp_v565m"
            )
            name = name_elem.text if name_elem else None

            # First check for "Access email" button
            get_email = await first_person.query_selector(
                'button.zp_qe0Li.zp_FG3Vz.zp_QMAFM.zp_h2EIO'
            )
            if get_email:
                logger.debug("Found Access email button, clicking it")
                await get_email.click()
                # Wait for email to appear after clicking
                await self.page.wait_for(selector="span.zp_xvo3G.zp_JTaUA", timeout=10)

            # Now try to get the email element (either direct or after clicking)
            try:
                email_elem = await first_person.query_selector(
                    "span.zp_xvo3G.zp_JTaUA"
                )
                if not email_elem:
                    email_elem = await first_person.query_selector(
                        "span.zp_xvo3G.zp_TTaaZ"
                    )
            except Exception as e:
                logger.debug(f"Error accessing email element: {str(e)}")
                email_elem = None

            email = email_elem.text if email_elem else None

            if name and email:
                logger.debug(
                    f"Successfully extracted contact info for first person: {name}, {email}"
                )
            else:
                logger.warning(
                    "Incomplete contact information extracted for first person"
                )

            return name, email
        except Exception as e:
            logger.error(
                f"Error extracting contact info: {str(e)}", exc_info=True
            )
            return None, None

    async def get_company_contacts(
        self, company_domain: str
    ) -> Optional[tuple[str, str]]:
        """Search for and retrieve contact information for the first person found for a company."""
        logger.info(f"Searching for contacts at domain: {company_domain}")
        search_url = (
            "https://app.apollo.io/#/people"
            "?sortAscending=false"
            "&sortByField=person_title_normalized"
            "&contactEmailStatusV2%5B%5D=verified"
            "&personDepartmentOrSubdepartments%5B%5D=executive"
            "&personDepartmentOrSubdepartments%5B%5D=founder"
            "&personDepartmentOrSubdepartments%5B%5D=information_technology_executive"
            "&personDepartmentOrSubdepartments%5B%5D=operations_executive"
            f"&page=1&qKeywords={company_domain}"
        )
        await self.page.get(url=search_url)

        # Check if results exist
        if await self.page.find(
            text="No people match your criteria", timeout=2
        ):
            logger.warning(f"No contacts found for domain: {company_domain}")
            return None, None

        return await self._extract_contact_info()

    async def close(self) -> None:
        """Clean up browser resources."""
        logger.info("Closing Apollo client")
        if self.page:
            await self.page.close()
        if self.browser:
            self.browser.stop()


async def get_apollo_emails(wellfound_output_df: pd.DataFrame) -> pd.DataFrame:
    """Process companies and retrieve contact information using Apollo."""
    logger.info(
        f"Starting Apollo email retrieval for {len(wellfound_output_df)} companies"
    )
    client = ApolloClient()
    await client.initialize()

    try:
        successful_lookups = 0
        for index, row in wellfound_output_df.iterrows():
            company_website = row["website"]
            logger.info(
                f"Processing company {index + 1}/{len(wellfound_output_df)}: {company_website}"
            )

            name, email = await client.get_company_contacts(row["website"])
            if name and email:
                wellfound_output_df.at[index, "contact_name"] = name
                wellfound_output_df.at[index, "email"] = email
                successful_lookups += 1
                logger.info(f"Found contact for {company_website}: {name}")
            else:
                logger.warning(f"No contact found for {company_website}")

        if not wellfound_output_df.empty:
            initial_count = len(wellfound_output_df)
            wellfound_output_df.dropna(subset=["email"], inplace=True)
            final_count = len(wellfound_output_df)
            logger.info(
                f"Email retrieval complete. Success rate: {successful_lookups}/{initial_count} companies"
            )
            logger.info(
                f"Removed {initial_count - final_count} companies without contact information"
            )

    except Exception:
        logger.error("Error during Apollo email retrieval", exc_info=True)
        raise
    finally:
        await client.close()

    return wellfound_output_df
