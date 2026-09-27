from fetchers.news import get_news
from rag.chunker import chunk_text 
from rag.embedder import embed_chunks
from rag.store import store_chunks

# TODO: move to config file
company_names = ["Evergy","The Southern Company", "Duke Energy", "Sempra", "Xcel Energy", "Pacific Gas & Electric"]

if __name__ == "__main__":
    from database.connection import conn
    cursor = conn.cursor()
    for company in company_names:
        print(f"Processing {company}")
        try:
            articles = get_news(company)
            for article in articles:
                cursor.execute("""
                SELECT id 
                FROM chunks 
                WHERE url = %s
                """, (article["url"],))
                row = cursor.fetchone()

                if row is None:
                    text = article["content"]
                    chunks = chunk_text(text)
                    pairs = embed_chunks(chunks)
                    article["company_name"] = company
                    store_chunks(pairs, article)
        except Exception as e:
            print(f"Error: {e} On Company: {company}")