"""
RAG Vector Store & Retrieval Engine for FraudLens AI.
Ingests trusted cybersecurity guidance (CISA, OWASP, NIST),
chunks text into semantic passages, and performs cosine similarity retrieval.
"""

import glob
import logging
import os
import re
from typing import List, Dict, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger("rag_vector_store")

DOC_METADATA = {
    "cisa_phishing_guidance.md": {
        "title": "CISA Phishing Defense & Incident Response Guidance",
        "organization": "Cybersecurity & Infrastructure Security Agency (CISA)",
        "source_url": "https://www.cisa.gov/topics/cyber-threats-and-advisories/phishing",
        "citation": "CISA Phishing Guidance (Alert AA22-216A)"
    },
    "owasp_phishing_prevention.md": {
        "title": "OWASP Phishing Defense and Web Application Guidance",
        "organization": "Open Web Application Security Project (OWASP)",
        "source_url": "https://owasp.org/www-community/attacks/Phishing",
        "citation": "OWASP Security Guidelines"
    },
    "nist_sp800_phishing_defense.md": {
        "title": "NIST SP 800-63B / SP 800-177 Phishing Resistance Standards",
        "organization": "National Institute of Standards and Technology (NIST)",
        "source_url": "https://csrc.nist.gov/publications/detail/sp/800-63b/final",
        "citation": "NIST Special Publication 800-63B / 800-177"
    }
}

class RAGVectorStore:
    def __init__(self, kb_dir: str = "backend/app/rag/knowledge_base"):
        self.kb_dir = kb_dir
        self.chunks: List[Dict[str, Any]] = []
        self.vectorizer: TfidfVectorizer = None
        self.tfidf_matrix = None
        self.is_indexed = False
        self.initialize()

    def initialize(self):
        # Find all markdown files in knowledge base
        pattern = os.path.join(self.kb_dir, "*.md")
        files = glob.glob(pattern)
        if not files:
            # Try alternate path if called from backend root
            alt_pattern = os.path.join("app/rag/knowledge_base", "*.md")
            files = glob.glob(alt_pattern)

        if not files:
            logger.warning(f"No knowledge base documents found in {self.kb_dir}")
            return

        all_chunks = []
        for fpath in files:
            filename = os.path.basename(fpath)
            meta = DOC_METADATA.get(filename, {
                "title": filename,
                "organization": "Cybersecurity Reference",
                "source_url": "https://csrc.nist.gov",
                "citation": filename
            })

            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    content = f.read()

                # Chunk by markdown headers or double newlines
                sections = re.split(r"\n(?=##?\s)", content)
                for idx, sec in enumerate(sections):
                    cleaned = sec.strip()
                    if len(cleaned) > 50:
                        all_chunks.append({
                            "chunk_id": f"{filename}#part-{idx}",
                            "content": cleaned,
                            "filename": filename,
                            "title": meta["title"],
                            "organization": meta["organization"],
                            "source_url": meta["source_url"],
                            "citation": meta["citation"]
                        })
            except Exception as e:
                logger.error(f"Error reading knowledge doc {fpath}: {e}")

        if all_chunks:
            self.chunks = all_chunks
            corpus = [c["content"] for c in self.chunks]
            self.vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
            self.tfidf_matrix = self.vectorizer.fit_transform(corpus)
            self.is_indexed = True
            logger.info(f"RAG Vector Store initialized with {len(self.chunks)} chunks across {len(files)} docs.")

    def retrieve(self, query: str, top_k: int = 3, min_score: float = 0.05) -> List[Dict[str, Any]]:
        """
        Retrieves top_k most relevant chunks for a user query.
        Returns empty list if store is unindexed or no matches meet threshold.
        """
        if not self.is_indexed or not self.vectorizer or not query.strip():
            return []

        try:
            query_vec = self.vectorizer.transform([query])
            sim_scores = cosine_similarity(query_vec, self.tfidf_matrix)[0]

            scored_indices = sorted(enumerate(sim_scores), key=lambda x: x[1], reverse=True)

            results = []
            for idx, score in scored_indices[:top_k]:
                if score >= min_score:
                    chunk_data = self.chunks[idx].copy()
                    chunk_data["similarity_score"] = round(float(score), 4)
                    results.append(chunk_data)

            return results
        except Exception as e:
            logger.error(f"Retrieval error: {e}")
            return []

# Singleton instance
rag_store_instance = RAGVectorStore()
