def chunk_text(text: str, chunk_size=500, overlap=80):
    words = text.split()
    chunks = []

    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk_words = words[start:end]
        chunk = " ".join(chunk_words)

        # Skip tiny chunks
        if len(chunk_words) > 50:
            chunks.append(chunk)

        start = end - overlap

    return chunks
