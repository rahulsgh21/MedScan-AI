"""Script to re-ingest all KB documents into ChromaDB."""
from app.services.vector_store import get_vector_store

store = get_vector_store()
store.ingest_data()
docs = store.collection.get()
print(f"\nTotal documents in KB: {len(docs['ids'])}")
for doc_id in docs['ids']:
    print(f"  - {doc_id}")
