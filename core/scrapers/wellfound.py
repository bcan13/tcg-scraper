import nodriver as uc
import pandas as pd
import csv
import os

# TODO: format better for remote
# TODO: add a filter for company size


async def get_jobs_wellfound():

    browser = await uc.start()
    
    # config, will move to config folder soon
    job_titles = ["data science", "software engineer", "machine learning engineer"]
    location = "san diego"
    file_name = 'wellfound_output.csv'
    
    # check if file exists, if so, read existing companies
    if os.path.exists(file_name):
        existing_companies = pd.read_csv(file_name)
        existing_companies = set(existing_companies['company_name'])
    else:
        existing_companies = set()

    # list to accumulate all company data
    all_companies = []

    for job in job_titles:
        
        search_url = f"https://wellfound.com/role/l/{job.replace(' ', '-')}/{location.replace(' ', '-')}"
        page = await browser.get(search_url)
        
        await page.wait_for(selector = '.pl-2.flex.flex-col')

        # get company div for each company on each job
        company_div = await page.query_selector_all('.pl-2.flex.flex-col')  # Adjust selectors if needed
        
        for company in company_div:
            company_name = await company.query_selector('h2.inline.text-md.font-semibold')
            company_desc = await company.query_selector('span.text-xs.text-neutral-1000')
            company_size = await company.query_selector('span.text-xs.italic.text-neutral-500')
            
            # if we already seen the company, continue
            if company_name.text in existing_companies:
                continue

            # store the data for the current company
            company_data = {
                "company_name": company_name.text if company_name else "",
                "description": company_desc.text.strip('"') if company_desc else "",
                "job_type": job,
                "size": company_size.text if company_size else "",
                "location": location
            }

            # append the company data to the list
            all_companies.append(company_data)


    for job in job_titles:
        
        search_url = f"https://wellfound.com/role/r/{job.replace(' ', '-')}"
        page = await browser.get(search_url)
        
        await page.wait_for(selector = '.pl-2.flex.flex-col')

        # get company div for each company on each job
        company_div = await page.query_selector_all('.pl-2.flex.flex-col')  # Adjust selectors if needed
        
        for company in company_div:
            company_name = await company.query_selector('h2.inline.text-md.font-semibold')
            company_desc = await company.query_selector('span.text-xs.text-neutral-1000')
            company_size = await company.query_selector('span.text-xs.italic.text-neutral-500')
            
            # if we already seen the company, continue
            if company_name.text in existing_companies:
                continue

            # store the data for the current company
            company_data = {
                "company_name": company_name.text if company_name else "",
                "description": company_desc.text.strip('"') if company_desc else "",
                "job_type": job,
                "size": company_size.text if company_size else "",
                "location": "remote"
            }

            # append the company data to the list
            all_companies.append(company_data)

    # write the data to a csv file
    all_companies = pd.DataFrame(all_companies)
    all_companies.to_csv(file_name, mode='a', header=not os.path.exists(file_name), index=False, quoting=csv.QUOTE_ALL)

    browser.stop()

    print('done')

uc.loop().run_until_complete(get_jobs_wellfound())
