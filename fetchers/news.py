import requests

class AuthError(Exception):
    pass

class RateLimitError(Exception):
    pass

class RateLimitExceededError(Exception):
    pass

class ServerError(Exception):
    pass

def _call_api(company_name: str):
    pass