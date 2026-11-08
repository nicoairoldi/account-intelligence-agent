from firecrawl import Firecrawl
from dotenv import load_dotenv
import os

load_dotenv()
firecrawl_api_key = os.environ["FIRECRAWL_API_KEY"]
client = Firecrawl(api_key=firecrawl_api_key)

# Scrape a website:
scrape_result = client.scrape(
    'https://www.prnewswire.com/news-releases/duke-energy-foundation-invests-180-000-in-workforce-training-to-support-growth-across-south-carolina-302865126.html', 
    formats=['markdown'],
    only_main_content=True,
    )
slice_markdown = scrape_result.markdown[0:500]
print(slice_markdown)
print(len(slice_markdown))
print("\n")
print(len(scrape_result.markdown))
print(scrape_result)
