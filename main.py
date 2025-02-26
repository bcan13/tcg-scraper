from core.scrapers.wellfound import get_jobs_wellfound
from core.apollo.apollo import get_apollo_emails

df = get_jobs_wellfound()
get_apollo_emails(df)
