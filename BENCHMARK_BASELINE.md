# Benchmark de Tiempo de Respuesta - IurisLex v2

**Generado:** 2026-04-17 09:33:52

## Resumen Ejecutivo

- **Total de queries:** 25
- **Exitosas:** 25 (100%)
- **Timeout:** 0 (0%)
- **Error:** 0 (0%)

### Métricas de Tiempo (queries exitosas)

| Métrica | Valor (ms) |
|---------|-----------|
| **Media** | 2404 |
| **Mediana (p50)** | 2041 |
| **P75** | 2059 |
| **P95** | 2077 |
| **P99** | 6243 |
| **Mín** | 2015 |
| **Máx** | 6834 |
| **Desv Est** | 1248 |

---

## Resultados por Categoría

### BÚSQUEDA_SIMPLE

- **Queries:** 5
- **Exitosas:** 5
- **Media:** 2039ms
- **P95:** 2038ms

### BÚSQUEDA_COMPLEJA

- **Queries:** 5
- **Exitosas:** 5
- **Media:** 2054ms
- **P95:** 2061ms

### BÚSQUEDA_CON_TYPOS

- **Queries:** 5
- **Exitosas:** 5
- **Media:** 2050ms
- **P95:** 2051ms

### BÚSQUEDA_MULTIPLE_ARTÍCULOS

- **Queries:** 5
- **Exitosas:** 5
- **Media:** 2038ms
- **P95:** 2047ms

### BÚSQUEDA_ESPECÍFICA

- **Queries:** 5
- **Exitosas:** 5
- **Media:** 3837ms
- **P95:** 6243ms

---

## Resultados Detallados

| # | Categoría | Query | Status | Tiempo (ms) | Artículo | Confianza |
|---|-----------|-------|--------|------------|---------|-----------|
| 1 | búsqueda_simple | ¿Cuáles son los derechos fundamentales? | success | 2031 | 5 | 50% |
| 2 | búsqueda_simple | ¿Qué es la soberanía nacional? | success | 2038 | 9 | 50% |
| 3 | búsqueda_simple | ¿Qué dice sobre la igualdad? | success | 2034 | 204 | 50% |
| 4 | búsqueda_simple | Habeas corpus | success | 2075 | 157 | 50% |
| 5 | búsqueda_simple | Libertad de expresión | success | 2015 | 20 | 50% |
| 6 | búsqueda_compleja | ¿Cuáles son los derechos fundamentales y cómo se p... | success | 2035 | 94 | 50% |
| 7 | búsqueda_compleja | ¿Qué procedimientos existen para proteger los dere... | success | 2077 | 57 | 50% |
| 8 | búsqueda_compleja | Explica la estructura y funciones de las tres rama... | success | 2059 | 279 | 50% |
| 9 | búsqueda_compleja | ¿Cuál es el rol del Congreso en la aprobación de l... | success | 2061 | 101 | 50% |
| 10 | búsqueda_compleja | ¿Qué mecanismos constitucionales existen para prot... | success | 2040 | 38 | 50% |
| 11 | búsqueda_con_typos | ¿Qué es la soveranía naciional? | success | 2051 | 9 | 50% |
| 12 | búsqueda_con_typos | habeas corpis | success | 2040 | 169 | 50% |
| 13 | búsqueda_con_typos | libertad de expresion | success | 2046 | 20 | 50% |
| 14 | búsqueda_con_typos | derechos fundamntales | success | 2073 | 44 | 50% |
| 15 | búsqueda_con_typos | consitución | success | 2041 | 91 | 50% |
| 16 | búsqueda_multiple_artículos | ¿Qué artículos hablan sobre los derechos de los ci... | success | 2048 | 258 | 50% |
| 17 | búsqueda_multiple_artículos | ¿Qué diferencia hay entre la nación y el territori... | success | 2047 | 364 | 50% |
| 18 | búsqueda_multiple_artículos | ¿Cuáles son los principios que rigen la actividad ... | success | 2037 | 230 | 50% |
| 19 | búsqueda_multiple_artículos | ¿Qué dicen los artículos sobre la participación po... | success | 2023 | 318 | 50% |
| 20 | búsqueda_multiple_artículos | ¿Cómo está organizada la rama ejecutiva? | success | 2033 | 195 | 50% |
| 21 | búsqueda_específica | Artículo 1 | success | 2031 | 1 | 50% |
| 22 | búsqueda_específica | Artículo 19 | success | 6834 | 19 | 50% |
| 23 | búsqueda_específica | Artículo 44 | success | 2032 | 44 | 50% |
| 24 | búsqueda_específica | Artículo 86 | success | 6243 | 86 | 50% |
| 25 | búsqueda_específica | Artículo 365 | success | 2047 | 365 | 50% |


---

## Interpretación

- **Línea Base:** Este benchmark establece la línea base para las optimizaciones
- **Meta Post-Optimización:** Reducir tiempo medio a <3000ms (40-50% mejora)
- **Queries Exitosas:** Se considera solo estas para cálculo de percentiles
- **Outliers:** Revisar queries con tiempo > p95 para identificar casos problemáticos

---

## Próximos Pasos

1. Implementar **Fase 1: Paralelizar búsquedas** (estimado -400-900ms)
2. Implementar **Fase 2: Caché de búsquedas** (estimado -500-1000ms para repetidas)
3. Implementar **Fase 3: Timeout Ollama + fallback** (protección contra bloqueos)
4. Re-ejecutar benchmark para comparar mejoras

**Archivo generado:** C:\Users\huver\Desktop\IurisLex_Pro\benchmark_results.json
