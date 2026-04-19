import sys
import os
from pathlib import Path

# Fix python path since this runs from project root
sys.path.append(str(Path(__file__).parent))

from app.services.vector_store import get_vector_store

kb = get_vector_store()
query = 'What does a high troponin level mean for the heart?'
print(f'\nQuery: {query}')
results = kb.search(query, top_k=1)
for i, r in enumerate(results):
    print(f'\nMatch {i+1} (Distance: {r["distance"]:.4f}) from {r["metadata"]["source"]}:')
    print('-'*50)
    print(r["content"][:400] + '...')
