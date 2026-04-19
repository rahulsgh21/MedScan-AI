"""
Vector Store / Medical Knowledge Base Service.

This handles loading our markdown files and reference ranges,
chunking them, and indexing them into ChromaDB for semantic search.

Interview talking point:
  "I separated the Knowledge Base ingestion from the API. 
   This allows us to update medical guidelines offline without 
   touching the runtime application."
"""

import os
import json
from pathlib import Path
import chromadb
from chromadb.utils import embedding_functions
from app.core.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class KnowledgeBase:
    """Manages the document ingestion and ChromaDB interaction."""

    def __init__(self):
        # Ensure the persist directory exists
        Path(settings.chroma_persist_dir).mkdir(parents=True, exist_ok=True)
        
        # Initialize ChromaDB client
        self.chroma_client = chromadb.PersistentClient(path=settings.chroma_persist_dir)
        
        # Use sentence-transformers embedding model
        # This downloads a small model (~80MB) on first run and runs locally
        self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=settings.embedding_model
        )
        
        # Get or create the collection
        self.collection = self.chroma_client.get_or_create_collection(
            name="medical_knowledge_pubmed_768",
            embedding_function=self.embedding_fn
        )
        logger.info(f"Connected to ChromaDB collection: 'medical_knowledge_pubmed_768' ({self.collection.count()} docs)")

    def ingest_data(self):
        """
        Load all medical documents from the knowledge directory and index them.
        In a production system, this would be an offline job.
        """
        logger.info("Starting knowledge base ingestion...")
        
        documents = []
        metadatas = []
        ids = []

        kb_dir = Path(settings.knowledge_base_dir)

        # 1. Ingest Biomarker Markdown Files
        biomarker_dir = kb_dir / "biomarker_info"
        if biomarker_dir.exists():
            for file_path in biomarker_dir.glob("*.md"):
                content = file_path.read_text(encoding="utf-8")
                # We chunk by file since they are small (~1 page each)
                # Production RAG would need a more sophisticated chunker (langchain RecursiveCharacterTextSplitter)
                doc_id = f"biomarker_{file_path.stem}"
                
                documents.append(content)
                metadatas.append({"source": file_path.name, "type": "biomarker_info"})
                ids.append(doc_id)
                logger.debug(f"Ingesting: {file_path.name}")

        # 2. Ingest Lifestyle Tips
        lifestyle_dir = kb_dir / "lifestyle_tips"
        if lifestyle_dir.exists():
            for file_path in lifestyle_dir.glob("*.md"):
                content = file_path.read_text(encoding="utf-8")
                doc_id = f"lifestyle_{file_path.stem}"
                
                documents.append(content)
                metadatas.append({"source": file_path.name, "type": "lifestyle_tips"})
                ids.append(doc_id)
                logger.debug(f"Ingesting: {file_path.name}")

        # Upsert everything into ChromaDB
        if documents:
            self.collection.upsert(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            logger.info(f"Ingestion complete. Vector store now has {self.collection.count()} documents.")
        else:
            logger.warning("No documents found to ingest!")

    def search(self, query: str, top_k: int = 3) -> list[dict]:
        """
        Perform a semantic (dense) search in ChromaDB.
        
        Args:
            query: The user query or biomarker context string
            top_k: Number of results to return
            
        Returns:
            List of dictionaries containing document content and metadata
        """
        if self.collection.count() == 0:
            logger.warning("Search called on empty vector store! Auto-ingesting...")
            self.ingest_data()

        results = self.collection.query(
            query_texts=[query],
            n_results=top_k
        )
        
        # Format results into a cleaner list of dicts
        formatted_results = []
        if results['documents'] and results['documents'][0]:
            for i in range(len(results['documents'][0])):
                formatted_results.append({
                    "content": results['documents'][0][i],
                    "metadata": results['metadatas'][0][i],
                    "distance": results['distances'][0][i] if 'distances' in results and results['distances'] else 0.0,
                    "id": results['ids'][0][i]
                })
        
        return formatted_results


# Singleton
_vector_store = None

def get_vector_store() -> KnowledgeBase:
    global _vector_store
    if _vector_store is None:
        _vector_store = KnowledgeBase()
    return _vector_store
