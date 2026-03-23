from __future__ import annotations

CHUNK_SIZE = 1500
OVERLAP = 150


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = OVERLAP) -> list[str]:
    """
    Split text into overlapping chunks of approximately chunk_size characters.
    Tries to split on paragraph/sentence boundaries where possible.
    """
    if len(text) <= chunk_size:
        return [text.strip()]

    chunks: list[str] = []
    start = 0

    while start < len(text):
        end = start + chunk_size

        if end >= len(text):
            chunks.append(text[start:].strip())
            break

        # Try to find a paragraph break near the end
        split_pos = text.rfind("\n\n", start, end)
        if split_pos == -1 or split_pos <= start:
            # Fall back to sentence break
            split_pos = text.rfind(". ", start, end)
        if split_pos == -1 or split_pos <= start:
            split_pos = end

        chunk = text[start:split_pos].strip()
        if chunk:
            chunks.append(chunk)
        start = max(split_pos - overlap, start + 1)

    return chunks
