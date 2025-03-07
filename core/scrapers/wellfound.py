from core.database.sqlite import add_company_seen, company_seen_before
import nodriver as uc
import pandas as pd
import csv
import os
import sys

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
)

from utils.parse_link import parse_link


# TODO: format better for remote
# TODO: add a filter for company size


async def get_jobs_wellfound():
    browser = await uc.start(no_sandbox=True)

    # config, will move to config folder soon
    job_titles = ["data science", "software engineer"]
    location = "san diego"
    max_company_size = 100

    # list to accumulate all company data
    all_companies = []

    for job in job_titles:
        search_url = f"https://wellfound.com/role/l/{job.replace(' ', '-')}/{location.replace(' ', '-')}"
        page = await browser.get(search_url)

        await page.wait_for(selector=".pl-2.flex.flex-col")

        # get company div for each company on each job
        company_div = await page.query_selector_all(
            ".pl-2.flex.flex-col"
        )  # Adjust selectors if needed

        for company in company_div:
            company_page = await company.query_selector("a.text-neutral-1000")
            company_name = await company_page.query_selector(
                "h2.inline.text-md.font-semibold"
            )
            company_desc = await company.query_selector(
                "span.text-xs.text-neutral-1000"
            )
            company_size = await company.query_selector(
                "span.text-xs.italic.text-neutral-500"
            )

            # if we already seen the company, continue
            exists = any(
                company["company_name"] == company_name.text
                for company in all_companies
            )

            if exists:
                continue

            # if company size is greater than max_company_size, continue
            if (
                "+" in company_size.text
                or int(company_size.text.split("-")[0]) > max_company_size
            ):
                continue

            # if we've emailed company before, continue
            if company_seen_before(company_name.text):
                continue

            # store the data for the current company
            company_data = {
                "company_name": company_name.text if company_name else "",
                "description": company_desc.text.strip('"')
                if company_desc
                else "",
                "job_type": job,
                "size": company_size.text if company_size else "",
                "location": location,
            }

            company_url = f"https://wellfound.com{company_page.attrs['href']}"
            company_page = await browser.get(company_url, new_tab=True)

            if await company_page.find(text="Page not found", timeout=1):
                await company_page.close()
                continue
            else:
                await company_page.wait_for(
                    selector="button.styles_websiteLink___Rnfc",
                    timeout=float("inf"),
                )

                company_website = await company_page.query_selector(
                    "button.styles_websiteLink___Rnfc"
                )
                company_data["website"] = (
                    parse_link(company_website.text)
                    if company_website
                    else "N/A"
                )

                add_company_seen(
                    company_name=company_data["company_name"],
                    description=company_data["description"],
                    job_type=company_data["job_type"],
                    size=company_data["size"],
                    location=company_data["location"],
                    website=company_data["website"],
                )

                # close the tab
                await company_page.close()

                # append the company data to the list
                all_companies.append(company_data)

    for job in job_titles:
        search_url = f"https://wellfound.com/role/r/{job.replace(' ', '-')}"
        page = await browser.get(search_url)

        await page.wait_for(selector=".pl-2.flex.flex-col")

        # get company div for each company on each job
        company_div = await page.query_selector_all(
            ".pl-2.flex.flex-col"
        )  # Adjust selectors if needed

        for company in company_div:
            company_page = await company.query_selector("a.text-neutral-1000")
            company_name = await company_page.query_selector(
                "h2.inline.text-md.font-semibold"
            )
            company_desc = await company.query_selector(
                "span.text-xs.text-neutral-1000"
            )
            company_size = await company.query_selector(
                "span.text-xs.italic.text-neutral-500"
            )

            # if we already seen the company, continue
            exists = any(
                company["company_name"] == company_name.text
                for company in all_companies
            )

            if exists:
                continue

            # if company size is greater than max_company_size, continue
            if (
                "+" in company_size.text
                or int(company_size.text.split("-")[0]) > max_company_size
            ):
                continue

            # if we've emailed company before, continue
            if company_seen_before(company_name.text):
                continue

            # store the data for the current company
            company_data = {
                "company_name": company_name.text if company_name else "",
                "description": company_desc.text.strip('"')
                if company_desc
                else "",
                "job_type": job,
                "size": company_size.text if company_size else "",
                "location": "remote",
            }

            company_url = f"https://wellfound.com{company_page.attrs['href']}"
            company_page = await browser.get(company_url, new_tab=True)

            if await company_page.find(text="Page not found", timeout=1):
                await company_page.close()
                continue
            else:
                await company_page.wait_for(
                    selector="button.styles_websiteLink___Rnfc",
                    timeout=float("inf"),
                )

                company_website = await company_page.query_selector(
                    "button.styles_websiteLink___Rnfc"
                )
                company_data["website"] = (
                    parse_link(company_website.text)
                    if company_website
                    else "N/A"
                )

                add_company_seen(
                    company_name=company_data["company_name"],
                    description=company_data["description"],
                    job_type=company_data["job_type"],
                    size=company_data["size"],
                    location=company_data["location"],
                    website=company_data["website"],
                )

                # close the tab
                await company_page.close()

                # append the company data to the list
                all_companies.append(company_data)

    # write the data to a csv file
    all_companies = pd.DataFrame(all_companies)

    browser.stop()

    return all_companies


# uc.loop().run_until_complete(get_jobs_wellfound())
