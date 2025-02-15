import nodriver as uc

async def get_jobs_indeed():
    browser = await uc.start()
    page = await browser.get('https://secure.indeed.com')

    email = await page.select('input[type="email"]')
    await email.send_keys('brcan@ucsd.edu')

    submit_email = await page.select('button[type="submit"]')
    await submit_email.click()

    await page.wait_for(text='Account settings', timeout=float('inf'))

    job_title = ["data science intern", "software engineer intern", "machine learning intern"]
    location = "san diego"

    for job in job_title:
        search_url = f"https://www.indeed.com/jobs?q={job.replace(' ', '+')}&l={location.replace(' ', '+')}"

        page = await browser.get(search_url)
        
        # Scrape job titles and companies on the current page
        job_elements = await page.select_all(selector='[class*="jobTitle"]')  # Adjust selectors if needed
        job_titles = []
        #companies = await page.query_selector_all('.companyName')  # Adjust selectors if needed
        
        for element in job_elements:
            print(element.children[0].children[0]['title'])

        print('---------------------------------')

    # print(job_titles)


        # jobs = []
        # for title, company in zip(job_titles, companies):
        #     job_title_text = await title.inner_text()
        #     company_name = await company.inner_text()
        #     jobs.append((job_title_text, company_name))
        
        # # Print job listings for the current page
        # for job in jobs:
        #     print(f"Job Title: {job[0]}")
        #     print(f"Company: {job[1]}")
        #     print("-" * 40)

        # # Check for a "Next" button to handle pagination
        # next_button = await page.query_selector('a[aria-label="Next"]')  # This selector can change
        # if next_button:
        #     await next_button.click()
        #     await page.wait_for_selector('.job_seen_beacon')  # Wait for the next page of jobs to load

    await page.sleep(float('inf'))

    browser.stop()

uc.loop().run_until_complete(get_jobs_indeed())
