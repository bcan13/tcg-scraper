import sys
import os
from pathlib import Path
from typing import List, Dict, Optional
import pandas as pd
import nodriver as uc
from dataclasses import dataclass
import logging

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
)

from core.database.sqlite import add_company_seen, company_seen_before
from utils.parse_link import parse_link



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




@dataclass
class WellfoundConfig:
    """Configuration settings for Wellfound scraper."""

    job_titles: List[str]
    locations: List[str]
    max_company_size: int
    base_url: str = "https://wellfound.com"


class CompanyScraper:
    """Handles scraping of company information from Wellfound."""

    def __init__(self, browser: uc.Browser, config: WellfoundConfig):
        self.browser = browser
        self.config = config

    async def _get_company_details(self, company_element) -> Optional[Dict]:
        """Extract basic company information from a company element."""
        try:
            company_page = await company_element.query_selector(
                "a.text-neutral-1000"
            )
            company_name = await company_page.query_selector(
                "h2.inline.text-md.font-semibold"
            )
            company_desc = await company_element.query_selector(
                "span.text-xs.text-neutral-1000"
            )
            company_size = await company_element.query_selector(
                "span.text-xs.italic.text-neutral-500"
            )

            if not all([company_name, company_desc, company_size]):
                logger.warning("Missing required company details from element")
                return None

            company_data = {
                "company_name": company_name.text,
                "description": company_desc.text.strip('"'),
                "size": company_size.text,
                "page_url": f"{self.config.base_url}{company_page.attrs['href']}",
            }
            logger.debug(
                f"Extracted company details: {company_data['company_name']}"
            )
            return company_data
        except Exception as e:
            logger.error(
                f"Error extracting company details: {str(e)}", exc_info=True
            )
            return None

    async def _get_company_website(self, company_url: str) -> Optional[str]:
        """Get company website from their profile page."""
        logger.debug(f"Fetching website from company profile: {company_url}")
        company_page = await self.browser.get(company_url, new_tab=True)

        try:
            if await company_page.find(text="Page not found", timeout=1):
                logger.warning(f"Company page not found: {company_url}")
                return None

            await company_page.wait_for(
                selector="button.styles_websiteLink___Rnfc",
                timeout=float("inf"),
            )

            website_elem = await company_page.query_selector(
                "button.styles_websiteLink___Rnfc"
            )
            website = parse_link(website_elem.text) if website_elem else None

            if website:
                logger.debug(f"Found company website: {website}")
            else:
                logger.warning(
                    f"No website found for company at: {company_url}"
                )

            return website
        finally:
            await company_page.close()

    def _should_process_company(self, company_data: Dict, size: str) -> bool:
        """Determine if company should be processed based on criteria."""
        company_name = company_data["company_name"]

        if (
            "+" in size
            or int(size.split("-")[0]) > self.config.max_company_size
        ):
            logger.debug(
                f"Company {company_name} excluded due to size: {size}"
            )
            return False

        if company_seen_before(company_name):
            logger.debug(
                f"Company {company_name} already processed previously"
            )
            return False

        return True

    async def _process_company(
        self, company_element, job_type: str, location: str
    ) -> Optional[Dict]:
        """Process a single company element and return its data."""
        company_data = await self._get_company_details(company_element)
        if not company_data:
            return None

        if not self._should_process_company(
            company_data, company_data["size"]
        ):
            return None

        website = await self._get_company_website(company_data["page_url"])
        if not website:
            return None

        company_data.update(
            {"job_type": job_type, "location": location, "website": website}
        )

        logger.info(
            f"Processing company: {company_data['company_name']} "
            f"({company_data['location']}, {company_data['job_type']})"
        )

        add_company_seen(
            company_name=company_data["company_name"],
            description=company_data["description"],
            job_type=company_data["job_type"],
            size=company_data["size"],
            location=company_data["location"],
            website=company_data["website"],
        )

        return company_data


class WellfoundScraper:
    """Main scraper class for Wellfound job listings."""

    def __init__(self, config: WellfoundConfig):
        self.config = config
        self.browser = None
        self.company_scraper = None

    async def initialize(self):
        """Initialize browser and company scraper."""
        self.browser = await uc.start(no_sandbox=True)
        self.company_scraper = CompanyScraper(self.browser, self.config)

    async def _get_companies_from_page(
        self, url: str, job_type: str, location: str
    ) -> List[Dict]:
        """Get all companies from a single search page."""
        logger.info(f"Scraping companies from: {url}")
        page = await self.browser.get(url)
        await page.wait_for(selector=".pl-2.flex.flex-col", timeout=float("inf"))

        companies = []
        company_elements = await page.query_selector_all(".pl-2.flex.flex-col")
        logger.info(f"Found {len(company_elements)} companies on page")

        for company_element in company_elements:
            company_data = await self.company_scraper._process_company(
                company_element, job_type, location
            )
            if company_data:
                companies.append(company_data)

        logger.info(
            f"Successfully processed {len(companies)} companies from page"
        )
        return companies

    def _build_search_url(
        self, job_title: str, location: Optional[str] = None
    ) -> str:
        """Build search URL based on job title and location."""
        if location:
            return f"{self.config.base_url}/role/l/{job_title.replace(' ', '-')}/{location.replace(' ', '-')}"
        return f"{self.config.base_url}/role/r/{job_title.replace(' ', '-')}?countryCodes[]=US"

    async def scrape(self) -> pd.DataFrame:
        """Main method to scrape all companies based on configuration."""
        logger.info("Starting Wellfound scraping process")
        all_companies = []

        try:
            # Scrape local jobs
            for job in self.config.job_titles:
                for location in self.config.locations:
                    logger.info(f"Scraping {job} positions in {location}")
                    url = self._build_search_url(job, location)
                    companies = await self._get_companies_from_page(
                        url, job, location
                    )
                    all_companies.extend(companies)

            # Scrape remote jobs
            for job in self.config.job_titles:
                logger.info(f"Scraping remote {job} positions")
                url = self._build_search_url(job)
                companies = await self._get_companies_from_page(
                    url, job, "remote"
                )
                all_companies.extend(companies)

        except Exception as e:
            logger.error("Error during scraping process", exc_info=True)
            raise
        finally:
            if self.browser:
                logger.info("Closing browser")
                self.browser.stop()

        logger.info(
            f"Scraping completed. Total companies processed: {len(all_companies)}"
        )
        return pd.DataFrame(all_companies)


async def get_jobs_wellfound() -> pd.DataFrame:
    """Entry point function to get jobs from Wellfound."""
    logger.info("Initializing Wellfound job scraper")
    config = WellfoundConfig(
        job_titles=["data science", "software engineer"],
        locations=["san diego"],
        max_company_size=100,
    )

    scraper = WellfoundScraper(config)
    await scraper.initialize()
    return await scraper.scrape()
