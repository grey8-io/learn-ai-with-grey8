# Document Chunking & Processing

In the previous lesson, you built a RAG pipeline that takes documents and feeds them to an LLM. But there is a problem: real documents are often thousands of words long. An entire PDF manual or a long web page will not fit in a single prompt, and even if it did, the model would struggle to find the relevant needle in that haystack.

The solution is **chunking** — splitting documents into smaller, meaningful pieces before storing them. Good chunking is one of the most important factors in RAG quality. Get it right, and your retriever finds precise, relevant passages. Get it wrong, and your system returns noisy, irrelevant context.

---

## Why Chunking Matters

LLMs have a limited context window — the maximum amount of text they can process at once. Even models with large windows perform better when given focused, relevant passages rather than massive blocks of text.

Chunking serves several purposes:

- **Fits context limits** — Each chunk must be small enough to include multiple chunks in a single prompt.
- **Improves retrieval precision** — Smaller chunks mean embeddings represent more specific content, leading to better similarity matches.
- **Reduces noise** — A 200-word passage about a specific topic is more useful than a 5,000-word document where only one paragraph is relevant.

---

## Chunk Size Tradeoffs

Choosing the right chunk size is a balancing act:

**Too small** (50-100 characters):
- Loses context and meaning
- A sentence fragment is not useful on its own
- More chunks to search through

**Too large** (5,000+ characters):
- Multiple topics mixed together
- Embeddings become too general
- Wastes context window space

**Sweet spot** (200-1,000 characters):
- Each chunk covers one concept or idea
- Enough context to be self-contained
- Embeddings are specific and meaningful

Most production systems use chunks of 300-800 characters, but the best size depends on your documents and use case. Always experiment.

```
  Too Small (50 words)      Just Right (200-500)     Too Large (2000 words)
  ┌────────┐                ┌──────────────────┐     ┌──────────────────────┐
  │ "Python│                │ "Python is a     │     │ (entire article      │
  │  is a  │                │  high-level      │     │  crammed into one    │
  │  high- │                │  programming     │     │  chunk — too much    │
  │  level"│                │  language used   │     │  noise dilutes the   │
  └────────┘                │  for web, data   │     │  relevant info)      │
  Missing context!          │  science, AI..." │     └──────────────────────┘
                            └──────────────────┘     Wastes tokens!
                            Meaningful unit
```

---

## Overlapping Chunks

When you split text at fixed positions, you risk cutting a sentence or idea in half. The concept you need might span two chunks, and neither chunk has the complete thought.

**Overlap** solves this by having each chunk share some text with its neighbors. If your chunk size is 500 characters with 50 characters of overlap, chunk 2 starts 450 characters after chunk 1 — the last 50 characters of chunk 1 are also the first 50 characters of chunk 2.

```
Chunk 1: [----------500 chars----------]
Chunk 2:                    [----------500 chars----------]
                            ^-- 50 char overlap
```

Typical overlap values are 10-20% of the chunk size.

---

## Chunking Strategies

### Fixed-Size Chunking

The simplest approach: split text every N characters. Fast and predictable, but ignores sentence boundaries and document structure.

### Sentence-Based Chunking

Split text into sentences first, then group N sentences per chunk. Respects natural language boundaries, so each chunk contains complete thoughts.

### Paragraph-Based Chunking

Split on double newlines (paragraph breaks). Paragraphs are natural units of thought in most documents. Small paragraphs can be merged together; large ones may need further splitting.

### Markdown-Aware Chunking

For structured documents (README files, documentation, wiki pages), split on headings (`#`, `##`, `###`). This preserves the document's logical structure and keeps related content together. Each chunk can include its heading for context.

### Recursive Chunking

Try the largest splitter first (sections), then fall back to paragraphs, then sentences, then characters. This is what LangChain's `RecursiveCharacterTextSplitter` does, and it works well for diverse document types.

---

## Metadata Preservation

Raw text chunks are useful, but annotated chunks are better. Adding metadata to each chunk helps with filtering, attribution, and debugging:

- **Source** — Which file or URL did this chunk come from?
- **Index** — What position is this chunk in the original document?
- **Character count** — How long is this chunk?
- **Word count** — Useful for estimating token counts.

When your RAG system returns sources, this metadata lets you point users to the exact file and section where the answer came from.

---

## Handling Different File Types

Different file types need different preprocessing before chunking:

- **Plain text (.txt)** — Ready to chunk directly.
- **Markdown (.md)** — Split on headings for structure-aware chunks.
- **PDF** — Extract text first (libraries like `pdfplumber` or `PyMuPDF`), then chunk. Be aware that PDF text extraction can be messy.
- **HTML** — Strip tags, extract text content, then chunk. Libraries like `BeautifulSoup` help here.

The chunking logic itself stays the same — you just need a preprocessing step to get clean text from each file type.

---

## Your Turn

In the exercise that follows, you will build four different chunking functions: fixed-size with overlap, sentence-based, paragraph-based, and markdown-aware. You will also build a metadata annotation function. These are real utilities you will use when building RAG systems.

Let's chunk some documents!
