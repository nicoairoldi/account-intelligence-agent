from fetchers.news import _call_api


company_name = 'The Southern Company'
response = _call_api(company_name)
print(len(response))
print(response)