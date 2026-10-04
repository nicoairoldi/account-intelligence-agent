"""Chunking module — splits article text into overlapping fixed-size token chunks."""

import tiktoken
CHUNK_SIZE = 400
OVERLAP = 80


def chunk_text(text: str) -> list[str]:
    """Split text into overlapping fixed-size chunks measured in tokens."""
    chunks = []
    encoder = tiktoken.encoding_for_model("text-embedding-3-small")
    token_list = encoder.encode(text) 
    for start in range(0, len(token_list), (CHUNK_SIZE-OVERLAP)):
        end = start + CHUNK_SIZE
        chunk = encoder.decode(token_list[start:end])
        if len(token_list[start:end]) > OVERLAP or start == 0:
            chunks.append(chunk)
    return chunks