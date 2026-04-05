"""
Exercise: Document Chunking Utilities — Solution
===================================================
"""
import re


def chunk_by_size(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """Split text into fixed-size overlapping chunks.

    Args:
        text: The input text to chunk.
        chunk_size: Maximum characters per chunk.
        overlap: Number of overlapping characters between chunks.

    Returns:
        A list of chunk strings.
    """
    if not text:
        return []

    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap

    return chunks


def chunk_by_sentences(
    text: str, sentences_per_chunk: int = 5, overlap: int = 1
) -> list[str]:
    """Split text into chunks of grouped sentences.

    Args:
        text: The input text to chunk.
        sentences_per_chunk: Number of sentences per chunk.
        overlap: Number of overlapping sentences between chunks.

    Returns:
        A list of chunk strings.
    """
    if not text:
        return []

    sentences = re.split(r"(?<=[.!?])\s+", text)
    sentences = [s for s in sentences if s.strip()]

    if not sentences:
        return []

    chunks = []
    start = 0
    step = sentences_per_chunk - overlap

    while start < len(sentences):
        group = sentences[start : start + sentences_per_chunk]
        chunks.append(" ".join(group))
        start += step

    return chunks


def chunk_by_paragraphs(text: str, max_chunk_size: int = 1000) -> list[str]:
    """Split text on paragraph breaks, merging small paragraphs.

    Args:
        text: The input text to chunk.
        max_chunk_size: Maximum characters per chunk.

    Returns:
        A list of chunk strings.
    """
    if not text:
        return []

    paragraphs = text.split("\n\n")
    paragraphs = [p.strip() for p in paragraphs if p.strip()]

    if not paragraphs:
        return []

    chunks = []
    current = paragraphs[0]

    for para in paragraphs[1:]:
        combined = current + "\n\n" + para
        if len(combined) <= max_chunk_size:
            current = combined
        else:
            chunks.append(current)
            current = para

    chunks.append(current)
    return chunks


def chunk_markdown(text: str, max_chunk_size: int = 1000) -> list[str]:
    """Split markdown text on headings, preserving structure.

    Args:
        text: The input markdown text to chunk.
        max_chunk_size: Maximum characters per chunk.

    Returns:
        A list of chunk strings.
    """
    if not text:
        return []

    sections = re.split(r"(?=^#{1,6}\s)", text, flags=re.MULTILINE)
    sections = [s.strip() for s in sections if s.strip()]

    if not sections:
        return []

    chunks = []
    for section in sections:
        if len(section) <= max_chunk_size:
            chunks.append(section)
        else:
            # Extract heading from first line
            lines = section.split("\n", 1)
            heading = lines[0]
            body = lines[1] if len(lines) > 1 else ""

            # Split body by paragraphs
            paragraphs = body.split("\n\n")
            paragraphs = [p.strip() for p in paragraphs if p.strip()]

            for para in paragraphs:
                chunks.append(heading + "\n\n" + para)

    return chunks


def add_chunk_metadata(
    chunks: list[str], source: str = "unknown"
) -> list[dict]:
    """Add metadata to each chunk.

    Args:
        chunks: A list of chunk strings.
        source: The source identifier for these chunks.

    Returns:
        A list of dicts with text, index, source, char_count, word_count.
    """
    result = []
    for i, chunk in enumerate(chunks):
        result.append(
            {
                "text": chunk,
                "index": i,
                "source": source,
                "char_count": len(chunk),
                "word_count": len(chunk.split()),
            }
        )
    return result


# ---------------------------------------------------------------------------
# Do not modify below this line
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    sample = (
        "This is the first sentence. This is the second sentence. "
        "This is the third sentence. This is the fourth sentence. "
        "This is the fifth sentence. This is the sixth sentence."
    )

    print("=== chunk_by_size ===")
    for i, chunk in enumerate(chunk_by_size(sample, chunk_size=60, overlap=10)):
        print(f"  Chunk {i}: {chunk!r}")

    print("\n=== chunk_by_sentences ===")
    for i, chunk in enumerate(chunk_by_sentences(sample, sentences_per_chunk=2)):
        print(f"  Chunk {i}: {chunk!r}")

    print("\n=== add_chunk_metadata ===")
    chunks = chunk_by_sentences(sample, sentences_per_chunk=3)
    for meta in add_chunk_metadata(chunks, source="sample.txt"):
        print(f"  [{meta['index']}] {meta['word_count']} words from {meta['source']}")
