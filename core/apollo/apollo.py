import nodriver as uc

async def get_apollo_emails(wellfound_output_df):
    browser = await uc.start(no_sandbox = True)

    page = await browser.get('https://app.apollo.io/#/login')

    await page.wait_for(selector='input[name="email"]')
    
    login_email = await page.select('button[class="zp-button zp_GGHzP zp_Kbe5T zp_PLp2D zp_rduLJ zp_g5xYz"]')
    await login_email.click()

    await page.wait_for(text = 'Recommended prospects', timeout = float('inf'))

    await page.get(url = f"https://app.apollo.io/#/people?sortAscending=false&sortByField=person_title_normalized&contactEmailStatusV2%5B%5D=verified&personDepartmentOrSubdepartments%5B%5D=executive&personDepartmentOrSubdepartments%5B%5D=founder&personDepartmentOrSubdepartments%5B%5D=information_technology_executive&personDepartmentOrSubdepartments%5B%5D=operations_executive&page=1&qKeywords=hashstack.finance")

    await page.sleep(float('inf'))

    browser.stop()

uc.loop().run_until_complete(get_apollo_emails())
