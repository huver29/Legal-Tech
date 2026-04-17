import numpy as np
import re
import time
import logging
from typing import List, Dict, Tuple
from dataclasses import dataclass
from sklearn.metrics.pairwise import cosine_similarity
from fuzzywuzzy import fuzz

logger = logging.getLogger(__name__)


# ================================
# 📦 RESULT STRUCTURE
# ================================

@dataclass
class SearchResult:
    article: Dict
    relevance_score: float
    semantic_score: float
    lexical_score: float
    fuzzy_score: float


# ================================
# 🔍 HYBRID SEARCH ENGINE
# ================================

class HybridSearchEngine:

    def __init__(self, articles: List[Dict], embeddings: np.ndarray):
        self.articles = articles
        self.embeddings = embeddings

    def _clean(self, text: str):
        return re.sub(r"[^\w\s]", "", text.lower())

    def _semantic(self, query_emb):
        return cosine_similarity([query_emb], self.embeddings)[0]

    def _lexical(self, query, text):
        q = set(self._clean(query).split())
        t = set(self._clean(text).split())
        return len(q & t) / (len(q) + 1e-5)

    def _fuzzy(self, query, text):
        return fuzz.partial_ratio(query, text) / 100

    def hybrid_search(self, query: str, query_emb, top_k=5):

        semantic_scores = self._semantic(query_emb)
        results = []

        for i, art in enumerate(self.articles):

            text = art.get("texto", "")

            lexical = self._lexical(query, text)
            fuzzy = self._fuzzy(query, text)

            score = (
                0.65 * semantic_scores[i] +
                0.25 * lexical +
                0.10 * fuzzy
            )

            results.append(SearchResult(
                article=art,
                relevance_score=score,
                semantic_score=semantic_scores[i],
                lexical_score=lexical,
                fuzzy_score=fuzzy
            ))

        results.sort(key=lambda x: x.relevance_score, reverse=True)
        return results[:top_k]


# ================================
# 🧱 CONTEXT BUILDER
# ================================

class ContextBuilder:

    @staticmethod
    def build(primary: Dict, related: List[Dict], max_chars=2500):

        context = f"""
ARTÍCULO PRINCIPAL:
Artículo {primary['number']}:
{primary['texto']}

ARTÍCULOS RELACIONADOS:
"""

        for art in related:
            context += f"\nArtículo {art['number']}: {art['texto'][:400]}..."

        return context[:max_chars]


# ================================
# 🧠 PROMPT BUILDER
# ================================

class PromptBuilder:

    @staticmethod
    def build(query: str, context: str):

        system = """
Eres experto en derecho constitucional colombiano.

REGLAS:
- SOLO usa los artículos dados
- NO inventes artículos
- SI no hay soporte suficiente: dilo explícitamente
- SIEMPRE cita artículos
"""

        user = f"""
CONTEXTO:
{context}

PREGUNTA:
{query}

FORMATO OBLIGATORIO:

1. Norma aplicable
2. Explicación
3. Artículos citados
4. Conclusión
"""

        return [
            {"role": "system", "content": system},
            {"role": "user", "content": user}
        ]


# ================================
# 🚫 VALIDADOR
# ================================

class ResponseValidator:

    @staticmethod
    def extract_articles(text):
        return re.findall(r"Artículo\s*(\d+)", text)

    @staticmethod
    def validate(response: str, retrieved: List[Dict], threshold=0.5):

        cited = ResponseValidator.extract_articles(response)
        retrieved_ids = [str(a["number"]) for a in retrieved]

        if not cited:
            return False, 0.0, "Sin citas"

        valid = [c for c in cited if c in retrieved_ids]

        confidence = len(valid) / len(cited)

        return confidence >= threshold, confidence, "OK"


# ================================
# ⚡ RAG PIPELINE COMPLETO
# ================================

class RAGPipeline:

    def __init__(self, search_engine, embedder, client, model, fallback_model):

        self.search_engine = search_engine
        self.embedder = embedder
        self.client = client
        self.model = model
        self.fallback_model = fallback_model

    def run(self, query: str):

        start = time.time()

        try:
            # 1️⃣ EMBEDDING
            query_emb = self.embedder(query)

            # 2️⃣ SEARCH
            results = self.search_engine.hybrid_search(query, query_emb, top_k=5)

            primary = results[0].article
            related = [r.article for r in results[1:]]

            # 3️⃣ CONTEXT
            context = ContextBuilder.build(primary, related)

            # 4️⃣ PROMPT
            messages = PromptBuilder.build(query, context)

            # 5️⃣ LLM
            try:
                response = self.client.chat(
                    model=self.model,
                    messages=messages
                )
            except Exception as e:
                logger.warning(f"Fallback activado: {e}")
                response = self.client.chat(
                    model=self.fallback_model,
                    messages=messages
                )

            content = response["message"]["content"]

            # 6️⃣ VALIDACIÓN
            is_valid, confidence, msg = ResponseValidator.validate(
                content,
                [r.article for r in results]
            )

            if not is_valid:
                content = "⚠️ Respuesta descartada por falta de soporte constitucional"

            return {
                "primary_article": primary,
                "related_articles": related,
                "llm_response": content,
                "validation": {
                    "is_valid": is_valid,
                    "confidence": confidence,
                    "message": msg
                },
                "metadata": {
                    "response_time_ms": int((time.time() - start) * 1000),
                    "results_found": len(results)
                }
            }

        except Exception as e:
            logger.error(f"Error en pipeline: {e}")
            raise