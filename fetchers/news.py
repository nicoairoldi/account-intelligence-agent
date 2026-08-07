import requests

class AuthError(Exception):
    def __init__(self, status_code):
        self.status_code = status_code
        super().__init__(f"Auth failed with status {status_code}")

class RateLimitError(Exception):
    def __init__(self, status_code):
        self.status_code = status_code
        super().__init__(f"Rate limited with status {status_code}")

class RateLimitExceededError(Exception):
    pass

class ServerError(Exception):
    def __init__(self, status_code):
        self.status_code = status_code
        super().__init__(f"Server error with status {status_code}") 

def _call_api(company_name: str) -> list[dict]:
    """ Call NewsAPI / everything endpoint for company_name

    Returns: 
        List of article dicts from the 'articles' field of the response
    
    Raises: 
        AuthError: 401 response (invalid API key)
        RateLimitError: 429 response (rate limit hit)
        ServerError: 500 response (NewsAPI upstream failure)

    """
    response = requests.get(f"https://newsapi.org/v2/everything?q={company_name}")
    if response.status_code == 200:
        return response.json()["articles"]
    elif response.status_code == 401:
        raise AuthError(status_code=401)
    elif response.status_code == 429:
        raise RateLimitError(status_code=429)
    elif response.status_code == 500:
        raise ServerError(status_code=500)
    
