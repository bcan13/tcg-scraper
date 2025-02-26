import nodriver as uc
import pandas as pd
import os

async def get_apollo_emails(wellfound_output_df):
    browser = await uc.start(no_sandbox = True)

    page = await browser.get('https://app.apollo.io/#/login')

    await page.wait_for(selector='input[name="email"]')
    
    login_email = await page.select('button[class="zp-button zp_GGHzP zp_Kbe5T zp_PLp2D zp_rduLJ zp_g5xYz"]')
    await login_email.click()

    await page.wait_for(text = 'Recommended prospects', timeout = float('inf'))

    for company_name, company_domain in zip(wellfound_output_df["company_name"], wellfound_output_df["website"]):
        await page.get(url = f"https://app.apollo.io/#/people?sortAscending=false&sortByField=person_title_normalized&contactEmailStatusV2%5B%5D=verified&personDepartmentOrSubdepartments%5B%5D=executive&personDepartmentOrSubdepartments%5B%5D=founder&personDepartmentOrSubdepartments%5B%5D=information_technology_executive&personDepartmentOrSubdepartments%5B%5D=operations_executive&page=1&qKeywords={company_domain}")

        does_not_exist = await page.find(text = 'No people match your criteria', timeout = 2)

        if does_not_exist:
            continue

        get_email = await page.find(text = 'Access email', timeout = 2)
        
        if get_email:

            await get_email.click()

            name = await page.query_selector('a.zp_p2Xqs.zp_v565m')
            name = name.text

            try:
                await page.wait_for(selector = 'span.zp_xvo3G.zp_JTaUA')
                email = await page.query_selector('span.zp_xvo3G.zp_JTaUA')
                email = email.text
            except Exception as e:
                await page.wait_for(selector = 'span.zp_xvo3G zp_TTaaZ')
                email = await page.query_selector('span.zp_xvo3G zp_TTaaZ')
                email = email.text

            print(f"{name} from {company_name} has email {email}")

        else:

            name = await page.query_selector('a.zp_p2Xqs.zp_v565m')
            name = name.text

            try:
                await page.wait_for(selector = 'span.zp_xvo3G.zp_JTaUA')
                email = await page.query_selector('span.zp_xvo3G.zp_JTaUA')
                email = email.text
            except Exception as e:
                await page.wait_for(selector = 'span.zp_xvo3G zp_TTaaZ')
                email = await page.query_selector('span.zp_xvo3G zp_TTaaZ')
                email = email.text

            print(f"{name} from {company_name} has email {email}")

    await page.sleep(float('inf'))

    browser.stop()
    
