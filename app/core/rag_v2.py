"""
Módulo RAG v2 mejorado con embeddings y búsqueda semántica.
Implementa recuperación de contexto constitucional robusto.
"""
import numpy as np
import re
import unicodedata
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache
from fuzzywuzzy import fuzz
from sklearn.metrics.pairwise import cosine_similarity

try:
    from sentence_transformers import SentenceTransformer
    HAS_SENTENCE_TRANSFORMERS = True
except ImportError:
    HAS_SENTENCE_TRANSFORMERS = False


@dataclass
class SearchResult:
    """Resultado de búsqueda con score de relevancia."""
    article_number: str
    article: Dict[str, str]
    relevance_score: float
    search_type: str  # 'semantic', 'lexical', 'fuzzy', 'hybrid'


class EmbeddingsLoader:
    """Carga y gestiona embeddings precomputados."""
    
    def __init__(self, embeddings_path: Path, articles: List[Dict[str, str]]):
        self.embeddings_path = embeddings_path
        self.articles = articles
        self.embeddings = None
        self.load_embeddings()
    
    def load_embeddings(self):
        """Carga embeddings desde archivo numpy."""
        if not self.embeddings_path.exists():
            print(f"⚠ Embeddings no encontrados en {self.embeddings_path}")
            return False
        
        try:
            self.embeddings = np.load(self.embeddings_path, allow_pickle=True)
            print(f"✓ Embeddings cargados: {self.embeddings.shape}")
            return True
        except Exception as e:
            print(f"ERROR cargando embeddings: {e}")
            return False
    
    def has_embeddings(self) -> bool:
        """Verifica si los embeddings están disponibles."""
        return self.embeddings is not None and len(self.embeddings) > 0
    
    def get_embedding(self, index: int) -> Optional[np.ndarray]:
        """Obtiene embedding de un artículo por índice."""
        if not self.has_embeddings() or index >= len(self.embeddings):
            return None
        return self.embeddings[index]


class QueryEmbedder:
    """Genera embeddings para queries usando sentence-transformers."""
    
    def __init__(self, model_name: str = "paraphrase-multilingual-MiniLM-L12-v2"):
        """Inicializa el generador de embeddings.
        
        Args:
            model_name: Modelo de sentence-transformers a usar
        """
        self.model_name = model_name
        self.model = None
        self.initialized = False
        
        if HAS_SENTENCE_TRANSFORMERS:
            try:
                print(f"Cargando modelo de embeddings: {model_name}...")
                self.model = SentenceTransformer(model_name)
                self.initialized = True
                embedding_dim = len(self.model.encode("prueba"))
                print(f"✓ Modelo de embeddings cargado (dimensión: {embedding_dim})")
            except Exception as e:
                print(f"⚠ Error cargando modelo de embeddings: {e}")
                self.initialized = False
        else:
            print("⚠ sentence-transformers no disponible. Búsqueda semántica desactivada.")
    
    def embed_query(self, query: str) -> Optional[np.ndarray]:
        """Genera embedding para una consulta.
        
        Args:
            query: Texto a convertir en embedding
            
        Returns:
            Array numpy con el embedding, o None si falla
        """
        if not self.initialized or not query:
            return None
        
        try:
            embedding = self.model.encode(query, convert_to_numpy=True)
            return embedding.astype(np.float32)
        except Exception as e:
            print(f"⚠ Error generando embedding: {e}")
            return None
    
    def embed_queries(self, queries: List[str]) -> List[Optional[np.ndarray]]:
        """Genera embeddings para múltiples consultas.
        
        Args:
            queries: Lista de textos
            
        Returns:
            Lista de embeddings numpy
        """
        if not self.initialized:
            return [None] * len(queries)
        
        try:
            embeddings = self.model.encode(queries, convert_to_numpy=True)
            return [e.astype(np.float32) for e in embeddings]
        except Exception as e:
            print(f"⚠ Error generando embeddings múltiples: {e}")
            return [None] * len(queries)


class TextNormalizer:
    """Normaliza texto para búsqueda."""
    
    @staticmethod
    def normalize(value: str) -> str:
        """Normaliza texto completo."""
        if not value:
            return ""
        normalized = unicodedata.normalize('NFKD', value.lower())
        without_diacritics = ''.join(
            ch for ch in normalized 
            if not unicodedata.combining(ch)
        )
        return re.sub(r'[^\w\s]+', ' ', without_diacritics).strip()
    
    @staticmethod
    def extract_article_number(query: str) -> Optional[str]:
        """Extrae número de artículo de una consulta."""
        match = re.search(r'\b(art\w*\.?\s*)?(\d{1,3})\b', query, re.IGNORECASE)
        if match:
            return match.group(2)
        return None


class HybridSearchEngine:
    """Motor de búsqueda híbrida: semántica + lexical."""
    
    def __init__(
        self, 
        articles: List[Dict[str, str]], 
        embeddings_loader: EmbeddingsLoader,
        semantic_weight: float = 0.6,
        lexical_weight: float = 0.4,
    ):
        self.articles = articles
        self.embeddings_loader = embeddings_loader
        self.semantic_weight = semantic_weight
        self.lexical_weight = lexical_weight
        self.normalizer = TextNormalizer()
        # Fase 4: Pre-indexar artículos para O(1) lookup
        self.articles_by_number = {a['number']: a for a in articles}
        # Fase 2: Caché de búsquedas recientes
        self.search_cache = {}
    
    def search_by_number(self, article_number: str) -> Optional[SearchResult]:
        """Búsqueda exacta por número de artículo."""
        for idx, article in enumerate(self.articles):
            if article['number'] == article_number:
                return SearchResult(
                    article_number=article_number,
                    article=article,
                    relevance_score=1.0,
                    search_type='exact'
                )
        return None
    
    def search_semantic(
        self, 
        query: str, 
        query_embedding: np.ndarray,
        top_k: int = 10
    ) -> List[SearchResult]:
        """Búsqueda semántica usando embeddings."""
        if not self.embeddings_loader.has_embeddings():
            return []
        
        if query_embedding is None or len(query_embedding) == 0:
            return []
        
        try:
            # Calcular similitud de coseno
            query_embedding_reshaped = query_embedding.reshape(1, -1)
            similarities = cosine_similarity(
                query_embedding_reshaped, 
                self.embeddings_loader.embeddings
            )[0]
            
            # Obtener top-k
            top_indices = np.argsort(similarities)[::-1][:top_k]
            
            results = []
            for idx in top_indices:
                score = float(similarities[idx])
                if score > 0.2:  # Threshold mínimo
                    results.append(SearchResult(
                        article_number=self.articles[idx]['number'],
                        article=self.articles[idx],
                        relevance_score=score,
                        search_type='semantic'
                    ))
            
            return results
        except Exception as e:
            print(f"ERROR en búsqueda semántica: {e}")
            return []
    
    def search_lexical(self, query: str, top_k: int = 10) -> List[SearchResult]:
        """Búsqueda lexical normalizada por tokens."""
        normalized_query = self.normalizer.normalize(query)
        if not normalized_query:
            return []
        
        query_tokens = set(normalized_query.split())
        
        matches = []
        for article in self.articles:
            search_text = article.get('search_text', '')
            article_tokens = set(search_text.split())
            
            # Calcular Jaccard similarity
            if article_tokens:
                intersection = len(query_tokens & article_tokens)
                union = len(query_tokens | article_tokens)
                score = intersection / union if union > 0 else 0
                
                if score > 0.1:
                    matches.append((score, article))
        
        matches.sort(key=lambda x: x[0], reverse=True)
        
        results = []
        for score, article in matches[:top_k]:
            results.append(SearchResult(
                article_number=article['number'],
                article=article,
                relevance_score=float(score),
                search_type='lexical'
            ))
        
        return results
    
    def search_fuzzy(self, query: str, top_k: int = 5) -> List[SearchResult]:
        """Búsqueda fuzzy para manejar typos."""
        results = []
        query_clean = self.normalizer.normalize(query)
        
        for article in self.articles:
            article_text = article.get('texto', '')[:100]  # Primeros 100 chars
            article_title = article.get('titulo_nombre', '')
            
            # Comparar con título y texto
            score_title = fuzz.ratio(query_clean, self.normalizer.normalize(article_title)) / 100
            score_text = fuzz.partial_ratio(query_clean, self.normalizer.normalize(article_text)) / 100
            
            score = max(score_title, score_text)
            
            if score > 0.6:
                results.append(SearchResult(
                    article_number=article['number'],
                    article=article,
                    relevance_score=score,
                    search_type='fuzzy'
                ))
        
        results.sort(key=lambda x: x.relevance_score, reverse=True)
        return results[:top_k]
    
    def hybrid_search(
        self,
        query: str,
        query_embedding: Optional[np.ndarray] = None,
        top_k: int = 10
    ) -> List[SearchResult]:
        """Búsqueda híbrida combinando semántica y lexical."""
        
        # 1. Primero intenta búsqueda exacta por número
        article_number = self.normalizer.extract_article_number(query)
        if article_number:
            exact_result = self.search_by_number(article_number)
            if exact_result:
                return [exact_result]
        
        # Fase 1: Paralelizar las 3 búsquedas
        semantic_results = {}
        lexical_results = {}
        fuzzy_results = {}
        
        with ThreadPoolExecutor(max_workers=3) as executor:
            # Enviar 3 búsquedas en paralelo
            semantic_future = executor.submit(
                self._get_semantic_dict, query, query_embedding, 20
            ) if query_embedding is not None else None
            
            lexical_future = executor.submit(
                self._get_lexical_dict, query, 20
            )
            
            fuzzy_future = executor.submit(
                self._get_fuzzy_dict, query, 10
            )
            
            # Recopilar resultados
            if semantic_future:
                semantic_results = semantic_future.result()
            lexical_results = lexical_future.result()
            fuzzy_results = fuzzy_future.result()
        
        # 2. Combinar scores
        combined_scores = {}
        
        for num in set(list(semantic_results.keys()) + list(lexical_results.keys()) + list(fuzzy_results.keys())):
            score = 0.0
            
            if num in semantic_results:
                score += semantic_results[num] * self.semantic_weight
            if num in lexical_results:
                score += lexical_results[num] * self.lexical_weight
            if num in fuzzy_results:
                score += fuzzy_results[num] * 0.2  # Peso menor para fuzzy
            
            if score > 0:
                combined_scores[num] = score
        
        # 3. Retornar top-k ordenados
        sorted_articles = sorted(
            combined_scores.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:top_k]
        
        results = []
        for num, score in sorted_articles:
            # Fase 4: Usar pre-indexed dictionary para O(1) lookup
            article = self.articles_by_number.get(num)
            if article:
                results.append(SearchResult(
                    article_number=num,
                    article=article,
                    relevance_score=score,
                    search_type='hybrid'
                ))
        
        return results
    
    def _get_semantic_dict(self, query: str, query_embedding: np.ndarray, top_k: int) -> Dict[str, float]:
        """Wrapper para búsqueda semántica paralela."""
        results = {}
        for result in self.search_semantic(query, query_embedding, top_k=top_k):
            results[result.article_number] = result.relevance_score
        return results
    
    def _get_lexical_dict(self, query: str, top_k: int) -> Dict[str, float]:
        """Wrapper para búsqueda lexical paralela."""
        results = {}
        for result in self.search_lexical(query, top_k=top_k):
            results[result.article_number] = result.relevance_score
        return results
    
    def _get_fuzzy_dict(self, query: str, top_k: int) -> Dict[str, float]:
        """Wrapper para búsqueda fuzzy paralela."""
        results = {}
        for result in self.search_fuzzy(query, top_k=top_k):
            results[result.article_number] = result.relevance_score
        return results
    
    def hybrid_search_cached(
        self,
        query: str,
        query_embedding: Optional[np.ndarray] = None,
        top_k: int = 10
    ) -> List[SearchResult]:
        """Búsqueda híbrida con caché local para queries recientes.
        Fase 2: Implementa caché LRU con TTL conceptual (limpieza manual).
        """
        # Normalizar query para caché
        query_normalized = query.lower().strip()
        query_hash = hashlib.md5(query_normalized.encode()).hexdigest()[:12]
        cache_key = f"{query_hash}_{top_k}"
        
        # Verificar caché
        if cache_key in self.search_cache:
            return self.search_cache[cache_key]
        
        # Si no está en caché, hacer búsqueda
        results = self.hybrid_search(query, query_embedding, top_k)
        
        # Guardar en caché (máximo 512 queries)
        if len(self.search_cache) >= 512:
            # Limpiar caché si excede límite (eliminar 50%)
            keys_to_remove = list(self.search_cache.keys())[:len(self.search_cache) // 2]
            for k in keys_to_remove:
                del self.search_cache[k]
        
        self.search_cache[cache_key] = results
        return results


class ResponseValidator:
    """Valida respuestas del LLM contra contenido constitucional."""
    
    @staticmethod
    def extract_article_references(response: str) -> List[str]:
        """Extrae referencias a artículos de la respuesta."""
        pattern = r'(?:Art\.?|Artículo)\s+(\d{1,3})'
        matches = re.findall(pattern, response, re.IGNORECASE)
        return list(set(matches))  # Únicas
    
    @staticmethod
    def validate_against_articles(
        response: str,
        query: str,
        retrieved_articles: List[Dict[str, str]],
        confidence_threshold: float = 0.3
    ) -> Tuple[bool, float, str]:
        """
        Valida que la respuesta esté basada en artículos recuperados.
        Retorna: (is_valid, confidence_score, message)
        """
        
        if not response or len(response) < 10:
            return False, 0.0, "Respuesta vacía o muy corta"
        
        # Extraer referencias de artículos
        referenced_articles = ResponseValidator.extract_article_references(response)
        
        if not referenced_articles:
            return False, 0.1, "La respuesta no cita artículos específicos"
        
        # Verificar que los artículos referenciados existen en los recuperados
        retrieved_numbers = {art['number'] for art in retrieved_articles}
        referenced_in_retrieved = set(referenced_articles) & retrieved_numbers
        
        coverage = len(referenced_in_retrieved) / len(referenced_articles) if referenced_articles else 0
        
        if coverage < 0.5:
            return False, coverage, "Artículos referenciados no corresponden al contexto"
        
        # Verificar que la respuesta menciona el tema de la consulta
        query_normalized = TextNormalizer.normalize(query)
        response_normalized = TextNormalizer.normalize(response)
        
        query_tokens = set(query_normalized.split())
        response_tokens = set(response_normalized.split())
        
        token_overlap = len(query_tokens & response_tokens) / len(query_tokens) if query_tokens else 0
        
        # Score final
        confidence = (coverage * 0.6 + token_overlap * 0.4)
        
        if confidence >= confidence_threshold:
            return True, confidence, "Respuesta validada"
        else:
            return False, confidence, f"Confianza baja: {confidence:.2%}"


class ContextBuilder:
    """Construye contexto para el LLM basado en búsqueda RAG."""
    
    @staticmethod
    def build_context(
        primary_article: Dict[str, str],
        related_articles: List[SearchResult],
        max_related: int = 5,
        max_chars: int = 2000
    ) -> Dict[str, str]:
        """Construye contexto estructurado para el LLM."""
        
        context = {
            'primary_article_number': primary_article['number'],
            'primary_article_title': primary_article.get('titulo_nombre', ''),
            'primary_article_chapter': primary_article.get('capitulo_nombre', ''),
            'primary_article_text': primary_article.get('texto', ''),
            'related_articles': [],
            'total_chars': 0
        }
        
        current_chars = len(context['primary_article_text'])
        
        for result in related_articles[:max_related]:
            if current_chars >= max_chars:
                break
            
            article = result.article
            article_text = article.get('texto', '')
            
            context['related_articles'].append({
                'number': article['number'],
                'title': article.get('titulo_nombre', ''),
                'text': article_text[:300],  # Máximo 300 chars por artículo
                'relevance_score': result.relevance_score,
                'search_type': result.search_type
            })
            
            current_chars += len(article_text[:300])
        
        context['total_chars'] = current_chars
        return context

    @staticmethod
    def format_for_llm(context: Dict[str, str]) -> str:
        """Formatea contexto como string para el prompt del LLM."""
        formatted = f"""## Contexto Constitucional

### Artículo Principal
**Artículo {context['primary_article_number']}**
Título: {context['primary_article_title']}
Capítulo: {context['primary_article_chapter']}

Texto:
{context['primary_article_text']}

### Artículos Relacionados
"""
        
        for related in context['related_articles']:
            formatted += f"""
- **Artículo {related['number']}**: {related['title']}
  Relevancia: {related['relevance_score']:.2%}
  Texto: {related['text']}...
"""
        
        return formatted
