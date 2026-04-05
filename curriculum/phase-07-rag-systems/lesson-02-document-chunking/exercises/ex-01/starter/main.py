"""
Exercise: Document Chunking Utilities
========================================
Complete the TODOs below.  When you're finished, run the tests:

    pytest ../tests/test_exercise.py

Build utility functions for splitting documents into chunks
using different strategies.
"""
import re


# TODO: Implement chunk_by_size(text, chunk_size=500, overlap=50)
#   - Split text into chunks of `chunk_size` characters
#   - Each chunk overlaps with the previous by `overlap` characters
#   - The first chunk starts at index 0
#   - Each subsequent chunk starts at (previous_start + chunk_size - overlap)
#   - Return a list of strings
#   - If text is empty, return an empty list


# TODO: Implement chunk_by_sentences(text, sentences_per_chunk=5, overlap=1)
#   - Split text into sentences using re.split(r'(?<=[.!?])\s+', text)
#   - Group sentences into chunks of `sentences_per_chunk` sentences
#   - Overlap by `overlap` sentences between consecutive chunks
#   - Join sentences in each chunk with a single space
#   - Return a list of strings
#   - If text is empty, return an empty list


# TODO: Implement chunk_by_paragraphs(text, max_chunk_size=1000)
#   - Split text on double newlines: text.split("\n\n")
#   - Strip whitespace from each paragraph, discard empty ones
#   - Merge consecutive small paragraphs into one chunk as long as
#     the combined length (joined with "\n\n") stays under max_chunk_size
#   - Return a list of strings
#   - If text is empty, return an empty list


# TODO: Implement chunk_markdown(text, max_chunk_size=1000)
#   - Split on markdown headings (lines starting with one or more #)
#   - Use re.split(r'(?=^#{1,6}\s)', text, flags=re.MULTILINE)
#   - Strip each section, discard empty ones
#   - If a section exceeds max_chunk_size, split it further by
#     double newlines (paragraphs), keeping the heading with each sub-chunk
#   - Return a list of strings
#   - If text is empty, return an empty list


# TODO: Implement add_chunk_metadata(chunks, source="unknown")
#   - Takes a list of chunk strings
#   - Returns a list of dicts, each with:
#     "text": the chunk string
#     "index": the chunk's position (0-based)
#     "source": the source parameter
#     "char_count": len(chunk)
#     "word_count": number of words (split on whitespace)


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
