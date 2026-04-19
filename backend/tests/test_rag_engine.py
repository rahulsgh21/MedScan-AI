"""
Test suite for RAG Engine and Vector Store.
"""

from app.services.vector_store import get_vector_store
from app.services.rag_engine import get_rag_engine

class TestRAGEngine:
    
    def test_vector_store_ingestion(self):
        """Test that vector store can ingest markdown files."""
        store = get_vector_store()
        store.ingest_data()
        
        # We should have the 4 biomarker info files and 1 lifestyle tip file
        docs = store.collection.get()
        assert len(docs["ids"]) >= 4
        print(f"\n✅ Vector store successfully ingested {len(docs['ids'])} docs")
        
    def test_hybrid_search(self):
        """Test that hybrid search retrieves relevant medical context."""
        engine = get_rag_engine()
        
        # Force a re-init of BM25 if needed
        engine._init_bm25()
        
        query = "What happens if my hemoglobin is low?"
        results = engine.hybrid_search(query, top_k=2)
        
        assert len(results) > 0
        
        # The top result should be hemoglobin.md
        top_result_source = results[0]["metadata"]["source"]
        assert "hemoglobin.md" in top_result_source
        
        print("\n✅ Hybrid Search returned the correct top document:")
        print(f"Query: '{query}' -> Top match: {top_result_source} (RRF Score: {results[0].get('rrf_score'):.3f})")

    def test_sparse_keyword_search(self):
        """Test that sparse search (BM25) picks up exact keywords."""
        engine = get_rag_engine()
        
        # 'polycythemia' is mentioned specifically in the hemoglobin doc
        query = "polycythemia"
        results = engine.sparse_search(query, top_k=1)
        
        assert len(results) > 0
        assert "hemoglobin.md" in results[0]["metadata"]["source"]
        
        print(f"\n✅ BM25 keyword search correctly found exact mismatch '{query}' in hemoglobin.md")
