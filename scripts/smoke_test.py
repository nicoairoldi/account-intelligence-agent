import requests
from dotenv import load_dotenv
from fetchers.news import _call_api



company_name = 'Evergy' 
response = _call_api(company_name)
print(response)