"""Chunking is pure, so it is tested without GCS or BigQuery."""
from scripts.build_doc_chunks import chunk_text


def test_short_text_is_one_chunk():
    assert chunk_text("a short manual page") == ["a short manual page"]


def test_long_text_splits_with_overlap():
    body = "x" * 2000
    chunks = chunk_text(body, size=800, overlap=100)
    assert len(chunks) == 3, chunks
    assert all(len(c) <= 800 for c in chunks)
    # Overlap exists so a sentence spanning a boundary is retrievable.
    assert chunks[0][-100:] == chunks[1][:100]


def test_empty_text_yields_no_chunks():
    assert chunk_text("") == []
    assert chunk_text("   ") == []
