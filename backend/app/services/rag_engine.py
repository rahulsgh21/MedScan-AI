"""
RAG Engine — Handles Hybrid Retrieval (Dense + Sparse).

Medical queries are unique. A dense embedding might know that 
"heart health" is related to "cardiology", but it might fail on 
exact terms like "HbA1c" or "RDW-CV".

Design Decision: HYBRID RETRIEVAL
1. Dense Search (ChromaDB): Good for semantic concepts ("I feel tired")
2. Sparse Search (BM25): Good for exact keywords ("MCHC is 32.5")
3. Reranker/Combiner: We use Reciprocal Rank Fusion (RRF) to combine both.

Interview talking point:
  "Standard RAG fails on medical acronyms because embeddings dilute them. 
   I implemented a Hybrid Retrieval system combining ChromaDB (dense) and 
   BM25 (sparse), fused with Reciprocal Rank Fusion to ensure we retrieve 
   the exact medical guideline when requested."
"""

from rank_bm25 import BM25Okapi
from app.services.vector_store import get_vector_store
from app.core.config import settings
from pathlib import Path
from app.utils.logger import get_logger

logger = get_logger(__name__)


class RAGEngine:
    """Hybrid Retrieval Augmented Generation Engine."""

    def __init__(self):
        self.vector_store = get_vector_store()
        self._bm25 = None
        self._bm25_docs = []
        self._init_bm25()

    def _init_bm25(self):
        """Initialize the BM25 sparse index from the same knowledge base."""
        logger.info("Initializing BM25 sparse index...")
        
        kb_dir = Path(settings.knowledge_base_dir)
        corpus = []
        self._bm25_docs = []
        
        for subdir in ["biomarker_info", "lifestyle_tips"]:
            target_dir = kb_dir / subdir
            if target_dir.exists():
                for file_path in target_dir.glob("*.md"):
                    content = file_path.read_text(encoding="utf-8")
                    
                    # Store the actual doc for retrieval
                    self._bm25_docs.append({
                        "content": content,
                        "metadata": {"source": file_path.name, "type": subdir},
                        "id": f"bm25_{file_path.stem}"
                    })
                    
                    # Tokenize for BM25 (simple whitespace tokenization for now)
                    # In production, use nltk or spacy tokenizer
                    tokenized_doc = content.lower().replace("\n", " ").split(" ")
                    corpus.append(tokenized_doc)
                    
        if corpus:
            self._bm25 = BM25Okapi(corpus)
            logger.info(f"BM25 index built with {len(corpus)} documents.")
        else:
            logger.warning("No documents found to build BM25 index.")

    def dense_search(self, query: str, top_k: int = 3) -> list[dict]:
        """Perform semantic search using ChromaDB."""
        return self.vector_store.search(query, top_k=top_k)

    def sparse_search(self, query: str, top_k: int = 3) -> list[dict]:
        """Perform keyword search using BM25."""
        if not self._bm25:
            return []
            
        tokenized_query = query.lower().split(" ")
        # Get scores for all docs
        doc_scores = self._bm25.get_scores(tokenized_query)
        
        # Sort and get top_k
        top_indices = sorted(range(len(doc_scores)), key=lambda i: doc_scores[i], reverse=True)[:top_k]
        
        results = []
        for idx in top_indices:
            if doc_scores[idx] > 0: # Only include if there's an actual match
                doc = self._bm25_docs[idx].copy()
                doc["score"] = float(doc_scores[idx])
                results.append(doc)
                
        return results

    def hybrid_search(self, query: str, top_k: int = 3) -> list[dict]:
        """
        Combine Dense and Sparse search results using Reciprocal Rank Fusion (RRF).
        RRF Score = 1 / (k + rank)  where k is usually 60.
        """
        dense_results = self.dense_search(query, top_k=top_k*2)
        sparse_results = self.sparse_search(query, top_k=top_k*2)
        
        # RRF Constants
        K = 60
        rrf_scores = {}
        unified_docs = {}
        
        # Add dense results to scoring
        for rank, doc in enumerate(dense_results):
            # We match by the metadata source name since IDs differ between dense and sparse
            doc_key = doc["metadata"]["source"]
            unified_docs[doc_key] = doc
            rrf_scores[doc_key] = 1.0 / (K + rank + 1)
            
        # Add sparse results to scoring
        for rank, doc in enumerate(sparse_results):
            doc_key = doc["metadata"]["source"]
            if doc_key not in unified_docs:
                unified_docs[doc_key] = doc
                rrf_scores[doc_key] = 0.0
            rrf_scores[doc_key] += 1.0 / (K + rank + 1)
            
        # Sort by RRF score descending
        sorted_keys = sorted(rrf_scores.keys(), key=lambda k: rrf_scores[k], reverse=True)
        
        # Return top_k
        final_results = []
        for key in sorted_keys[:top_k]:
            doc = unified_docs[key]
            doc["rrf_score"] = rrf_scores[key]
            final_results.append(doc)
            
        logger.debug(f"Hybrid search returned {len(final_results)} results for query: '{query}'")
        return final_results


# Singleton implementation
_rag_engine = None

def get_rag_engine() -> RAGEngine:
    global _rag_engine
    if _rag_engine is None:
        _rag_engine = RAGEngine()
    return _rag_engine
