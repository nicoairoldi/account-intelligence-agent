"""Retrieve Module - Retrieves the relevant data for the query from the database"""
from database.connection import conn
from rag.embedder import embed_chunks

def retrieve_chunks(query: str, company_name: str, top_k: int = 5) -> list[dict]:
    """Retrieves the chunks based on the cosine distance from the query text"""
    question_vect = embed_chunks([query])
    cursor = conn.cursor()
    cursor.execute("""
        SELECT chunk_text, title, source_name, published_at, url
        FROM chunks
        WHERE company_name = %s
        ORDER BY vector <=> %s
        LIMIT %s
        """,  (company_name, str(question_vect[0][1]), top_k))
    
    rows = cursor.fetchall()
    results = []
    for row in rows:
        to_insert = {}
        to_insert["chunk_text"] = row[0]
        to_insert["title"] = row[1]
        to_insert["source_name"] = row[2]
        to_insert["published_at"] = row[3]
        to_insert["url"] = row[4]
        results.append(to_insert)
    cursor.close()
    return results
    