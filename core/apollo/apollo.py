import nodriver as uc
import pandas as pd
from typing import Optional


class ApolloClient:
    def __init__(self):
        self.browser = None
        self.page = None

    async def initialize(self) -> None:
        """Initialize the browser and login to Apollo."""
        self.browser = await uc.start(no_sandbox=True)
        self.page = await self.browser.get("https://app.apollo.io/#/login")
        await self._login()

    async def _login(self) -> None:
        """Handle Apollo login process."""
        await self.page.wait_for(
            selector='input[name="email"]', timeout=float("inf")
        )
        login_email = await self.page.select(
            'button[class="zp-button zp_GGHzP zp_Kbe5T zp_PLp2D zp_rduLJ zp_g5xYz"]'
        )
        await login_email.click()
        await self.page.wait_for(text="Quick search", timeout=float("inf"))

    async def _extract_contact_info(self) -> Optional[tuple[str, str]]:
        """Extract name and email from the current page."""
        try:
            name_elem = await self.page.query_selector("a.zp_p2Xqs.zp_v565m")
            name = name_elem.text if name_elem else None

            try:
                await self.page.wait_for(selector="span.zp_xvo3G.zp_JTaUA")
                email_elem = await self.page.query_selector(
                    "span.zp_xvo3G.zp_JTaUA"
                )
            except Exception:
                await self.page.wait_for(selector="span.zp_xvo3G zp_TTaaZ")
                email_elem = await self.page.query_selector(
                    "span.zp_xvo3G zp_TTaaZ"
                )

            email = email_elem.text if email_elem else None
            return name, email
        except Exception as e:
            print(f"Error extracting contact info: {e}")
            return None, None

    async def get_company_contacts(
        self, company_domain: str
    ) -> Optional[tuple[str, str]]:
        """Search for and retrieve contact information for a company."""
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
            return None, None

        # Try to access email if needed
        get_email = await self.page.find(text="Access email", timeout=2)
        if get_email:
            await get_email.click()

        return await self._extract_contact_info()

    async def close(self) -> None:
        """Clean up browser resources."""
        if self.page:
            await self.page.close()
        if self.browser:
            self.browser.stop()


async def get_apollo_emails(wellfound_output_df: pd.DataFrame) -> pd.DataFrame:
    """Process companies and retrieve contact information using Apollo."""
    client = ApolloClient()
    await client.initialize()

    try:
        for index, row in wellfound_output_df.iterrows():
            name, email = await client.get_company_contacts(row["website"])
            if name and email:
                wellfound_output_df.at[index, "contact_name"] = name
                wellfound_output_df.at[index, "email"] = email

        if not wellfound_output_df.empty:
            wellfound_output_df.dropna(subset=["email"], inplace=True)

    finally:
        await client.close()

    return wellfound_output_df
