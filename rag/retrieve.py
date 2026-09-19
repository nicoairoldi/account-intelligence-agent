"""Retrieve Module - Retrieves the relevant data for the query from the database"""
from database.connection import conn
from rag.embedder import embed_chunks

def retrieve_chunks(query: str, company_name: str, top_k: int = 5) -> list[str]:
    """Retrieves the chunks based on the cosine distance from the query text"""
    question_vect = embed_chunks([query])
    cursor = conn.cursor()
    cursor.execute("""
        SELECT chunk_text, title, source_name, published_at
        FROM chunks
        WHERE company_name = %s
        ORDER BY vector <=> %s
        LIMIT %s
        """,  (company_name, str(question_vect[0][1]), top_k))
    
    rows = cursor.fetchall()
    results = []
    for row in rows:
        results.append(f"{row[1]} - {row[2]} ({row[3]})\n{row[0]}")
    cursor.close()
    return results
    