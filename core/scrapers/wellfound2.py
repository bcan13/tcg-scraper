import nodriver as uc
import pandas as pd
import csv
import os

#config
my_job_titles = ["data science", "software engineer", "machine learning engineer"]
my_location = "san diego"
my_file_name = 'wellfound_output.csv'
my_max_company_size = 100

#start browser
async def initialize_browser():
  return await uc.start(no_sandbox=True)
  
#load existing companies, return empty set if none
def load_existing_companies(file_name):
    if os.path.exists(file_name):
      existing_companies = pd.read_csv(file_name)
      return set(existing_companies['company_name'])
    else:
      return set()

#get company data from webpage
async def fetch_company_data(page, job, location, existing_companies, max_company_size):
    company_div = await page.query_selector_all('.pl-2.flex.flex-col')
    
  #list to accumulate all company data
    companies = []

  #iterate over each company div
    for company in company_div:
      
      #extracts company name using CSS selector, extracts company name, extracts company size
        company_name = await company.query_selector('h2.inline.text-md.font-semibold')
        company_desc = await company.query_selector('span.text-xs.text-neutral-1000')
        company_size = await company.query_selector('span.text-xs.italic.text-neutral-500')
       
      #if we already seen the company, continue
        if company_name.text in existing_companies:
            continue
          
      #if company size is greater than max_company_size, continue
        if '+' in company_size.text or int(company_size.text.split('-')[0]) > max_company_size:
            continue
          
       #store the data for the current company, append data to list
        companies.append({
            "company_name": company_name.text if company_name else "",
            "description": company_desc.text.strip('"') if company_desc else "",
            "job_type": job,
            "size": company_size.text if company_size else "",
            "location": location
        })

    return companies
  
#scrape jobs
async def scrape_jobs(browser, job_titles, location, file_name, max_company_size):
    existing_companies = load_existing_companies(file_name)

  #list to accumulate company data
    all_companies = []
  
  #iterate over each job title
    for job in job_titles:

      #constructing and navigating search URL
        search_url = f"https://wellfound.com/role/l/{job.replace(' ', '-')}/{location.replace(' ', '-')}"
        page = await browser.get(search_url)

      #wait for company divs to load
        await page.wait_for(selector='.pl-2.flex.flex-col')

      #adds scraped companies to list
        all_companies.extend(await fetch_company_data(page, job, location, existing_companies, max_company_size))

     
    return all_companies

#save to CSV
def save_to_csv(companies, file_name):
    df = pd.DataFrame(companies)
    df.to_csv(file_name, mode='a', header=not os.path.exists(file_name), index=False, quoting=csv.QUOTE_ALL)

#main function body 
async def get_jobs_wellfound():
    browser = await initialize_browser()
    companies = await scrape_jobs(browser, my_job_titles, my_location, my_file_name, my_max_company_size)
    save_to_csv(companies, my_file_name)
    await browser.stop()
    print('done')

uc.loop().run_until_complete(get_jobs_wellfound())
