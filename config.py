import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
SLACK_WEBHOOK_URL = os.environ["SLACK_WEBHOOK_URL"]

CLIENTS = [
    {"name": "HiAuto", "source_type": "jina", "url": "https://hi.auto/company/careers/"},
    {"name": "SupportYourApp", "source_type": "dou", "url": "https://jobs.dou.ua/companies/supportyourapp/vacancies/"},
    {"name": "SupportYourApp", "source_type": "jina", "url": "https://apply.workable.com/supportyourapp/#jobs"},
    {"name": "AltexSoft", "source_type": "dou", "url": "https://jobs.dou.ua/companies/altexsoft/vacancies/"},
    {"name": "AltexSoft", "source_type": "altexsoft"},
    {"name": "T-Pro", "source_type": "jina", "url": "https://info.tpro.io/careers"},
    {"name": "ABTO", "source_type": "jina", "url": "https://careers.abtosoftware.com/vacancies/"},
    {"name": "ABTO", "source_type": "dou", "url": "https://jobs.dou.ua/companies/abto-llc/vacancies/"},
]
