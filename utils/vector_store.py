import os
import numpy as np
from typing import List, Tuple
from langchain_openai import OpenAIEmbeddings
from langchain.schema import Document
from config import Config
from thefuzz import process as fuzz_process

class VectorStore:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(
            api_key=Config.OPENAI_API_KEY,
            model=Config.EMBEDDING_MODEL
        )
        self.documents = []
        self.document_embeddings = []

    def create_vector_store(self, text_chunks: List[str], pdf_filename: str):
        """Create in-memory vector store from text chunks using simple cosine similarity"""
        documents = [
            Document(
                page_content=chunk,
                metadata={"source": pdf_filename, "chunk_id": i}
            )
            for i, chunk in enumerate(text_chunks)
        ]
        self.documents = documents
        
        # Generate embeddings for all documents
        print(f"Generating embeddings for {len(documents)} documents...")
        texts = [doc.page_content for doc in documents]
        self.document_embeddings = self.embeddings.embed_documents(texts)
        
        print(f"Created simple vector store with {len(documents)} documents")

    def cosine_similarity(self, vec1, vec2):
        """Calculate cosine similarity between two vectors"""
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0
        
        return dot_product / (norm1 * norm2)

    def fuzzy_keyword_search(self, query: str) -> Tuple[str, float]:
        """Find the closest chunk by fuzzy keyword match if vector search fails"""
        if not self.documents:
            return None, 0
        
        choices = [doc.page_content for doc in self.documents]
        best_match, score = fuzz_process.extractOne(query, choices)
        return best_match, score / 100.0

    def similarity_search(self, query: str, k: int = 3) -> List[Tuple[Document, float]]:
        """Search for similar documents using cosine similarity"""
        if not self.documents or not self.document_embeddings:
            print("Vector store not initialized")
            return []

        try:
            # Generate embedding for the query
            query_embedding = self.embeddings.embed_query(query)
            
            # Calculate similarities
            similarities = []
            for i, doc_embedding in enumerate(self.document_embeddings):
                similarity = self.cosine_similarity(query_embedding, doc_embedding)
                # Convert similarity to distance (lower is better)
                distance = 1 - similarity
                similarities.append((self.documents[i], distance, similarity))
            
            # Sort by similarity (highest first) and take top k
            similarities.sort(key=lambda x: x[2], reverse=True)
            results = [(doc, distance) for doc, distance, _ in similarities[:k]]
            
            print(f"Found {len(results)} similar documents for query: '{query[:50]}...'")
            for i, (doc, score) in enumerate(results):
                print(f"  Result {i+1}: Score={score:.4f}, Content preview: '{doc.page_content[:100]}...'")

            # Check if results are relevant enough
            if not results or all(score >= Config.SIMILARITY_THRESHOLD for _, score in results):
                print("No relevant vector match, using fuzzy keyword search fallback.")
                best_match, fuzzy_score = self.fuzzy_keyword_search(query)
                if best_match:
                    doc = Document(page_content=best_match, metadata={"source": "fuzzy_fallback"})
                    return [(doc, 1-fuzzy_score)]

            return results

        except Exception as e:
            print(f"Error in similarity search: {e}")
            return []

    def is_relevant_to_pdf(self, query: str, threshold: float = None) -> bool:
        """Check if query is relevant to PDF content"""
        if threshold is None:
            threshold = Config.SIMILARITY_THRESHOLD
            
        results = self.similarity_search(query, k=1)
        if not results:
            print("No results found for relevance check")
            return False

        _, score = results[0]
        is_relevant = score < threshold
        print(f"Relevance check - Query: '{query[:50]}...', Score: {score:.4f}, Threshold: {threshold}, Relevant: {is_relevant}")
        return is_relevant
