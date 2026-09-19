"""Embedding module - embeds the text as vectors and return a list tuple with the text and vector"""
import openai

client = openai.OpenAI()
MODEL="text-embedding-3-small"


def embed_chunks(chunks: list[str]) -> list[tuple]:
    """Calls the opapi client and verctorizes the chunks and return the tuple of text with its vector pair"""
    text_vector = []
    response = client.embeddings.create(
        model=MODEL,
        input = chunks,
        )
    for vec in response.data:
        pair = (chunks[vec.index], vec.embedding)
        text_vector.append(pair)
    return text_vector 