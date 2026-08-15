"""Extract the GCS PDF corpus into mining_data.doc_chunks.

The corpus is read from GCS directly. mining_data.unstructured_docs_metadata
is NOT used: every file_path it carries resolves to nothing, and its
chunk_count sums to 3,392 against a real corpus of roughly 38 chunks.
"""
from __future__ import annotations

import io

from google.cloud import bigquery, storage
from pypdf import PdfReader

BUCKET = "mining-knowledge-base"
TABLE = "mining_data.doc_chunks"
SCHEMA = [
    bigquery.SchemaField("doc_id", "STRING"),
    bigquery.SchemaField("folder", "STRING"),
    bigquery.SchemaField("file_name", "STRING"),
    bigquery.SchemaField("chunk_index", "INT64"),
    bigquery.SchemaField("chunk_text", "STRING"),
]


def chunk_text(text: str, size: int = 800, overlap: int = 100) -> list[str]:
    """Split text into overlapping windows. Overlap keeps a sentence that
    spans a boundary retrievable from either side."""
    body = text.strip()
    if not body:
        return []
    if len(body) <= size:
        return [body]
    step = size - overlap
    return [body[i:i + size] for i in range(0, len(body) - overlap, step)]


def extract(blob) -> str:
    reader = PdfReader(io.BytesIO(blob.download_as_bytes()))
    return "\n".join((page.extract_text() or "") for page in reader.pages)


def rows() -> list[dict]:
    client = storage.Client()
    out = []
    for blob in client.list_blobs(BUCKET):
        if not blob.name.lower().endswith(".pdf"):
            continue
        folder, _, file_name = blob.name.rpartition("/")
        for index, chunk in enumerate(chunk_text(extract(blob))):
            out.append({
                "doc_id": blob.name,
                "folder": folder,
                "file_name": file_name,
                "chunk_index": index,
                "chunk_text": chunk,
            })
    return out


def main() -> None:
    data = rows()
    if not data:
        raise SystemExit("no chunks extracted; refusing to write an empty table")
    client = bigquery.Client(location="US")
    job = client.load_table_from_json(
        data,
        TABLE,
        job_config=bigquery.LoadJobConfig(
            schema=SCHEMA, write_disposition="WRITE_TRUNCATE"
        ),
    )
    job.result()
    print(f"loaded {len(data)} chunks from {len({r['doc_id'] for r in data})} documents")


if __name__ == "__main__":
    main()
