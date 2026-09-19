""" Store Module - Stores the chunks & vector in the database with the info from the article"""
from database.connection import conn
import uuid

def store_chunks(pairs: list[tuple], article: dict) -> None:
    """Batch stores the chunk in the database """
    article_id = str(uuid.uuid4())
    cursor = conn.cursor()
    for i, pair in enumerate(pairs):
        cursor.execute("""
        INSERT INTO chunks (article_id, chunk_index, title, company_name, source_name, url, chunk_text, vector, published_at) 
        Values (%s, %s, %s, %s, %s, %s, %s, %s ,%s )""", 
        (article_id, i, article["title"], article["company_name"], article["source"]["name"], article["url"], pair[0], str(pair[1]), article["publishedAt"]) )
    conn.commit()
    cursor.close()
