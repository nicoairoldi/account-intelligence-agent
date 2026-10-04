import requests
from dotenv import load_dotenv
import time
import os

load_dotenv()
api_key = os.environ["NEWSAPI_KEY"]
BACKOFF_SECONDS = [3, 6, 12]   # at module level


class AuthError(Exception):
    def __init__(self, status_code):
        self.status_code = status_code
        super().__init__(f"Auth failed with status {status_code}")

class RateLimitError(Exception):
    def __init__(self, status_code):
        self.status_code = status_code
        super().__init__(f"Rate limited with status {status_code}")

class RetryExhaustedError(Exception):
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
    url = f"https://newsapi.org/v2/everything?q={company_name}"
    # Auth via header, not query param — keeps key out of logs.
    response = requests.get(url, headers={'X-Api-Key': api_key})
    if response.status_code == 200:
        return response.json()["articles"]
    elif response.status_code == 401:
        raise AuthError(status_code=401)
    elif response.status_code == 429:
        raise RateLimitError(status_code=429)
    elif response.status_code == 500:
        raise ServerError(status_code=500)
    


def get_news(company_name: str) -> list[dict]:
    for attempt in range(4):
        try:
            return _call_api(company_name)
        except (RateLimitError, ServerError) as e:
                last_error = e
                if attempt < 3:
                    time.sleep(BACKOFF_SECONDS[attempt])
    raise RetryExhaustedError() from last_error