# ✅ CHECKLIST DE IMPLEMENTACIÓN Y DESPLIEGUE - IurisLex v2

## 🔍 Pre-Requisitos (Verificar antes de iniciar)

- [x] Python 3.8+ instalado
- [x] Ollama instalado y disponible en máquina
- [x] Acceso a terminal/PowerShell
- [x] Datos constitucionales cargados (CSV)
- [x] Embeddings disponibles (.npy)

---

## 📦 Paso 1: Preparación del Ambiente

### 1.1 Instalar Python (si es necesario)
```bash
# Verificar versión
python --version  # Debe ser >= 3.8
```

### 1.2 Crear virtual environment (Recomendado)
```bash
# En el directorio del proyecto
python -m venv .venv

# Activar
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
```

**Estado:** ☐ Completado

---

## 📚 Paso 2: Instalar Dependencias

### 2.1 Instalar paquetes

```bash
cd c:\Users\huver\Desktop\IurisLex_Pro
pip install -r requirements.txt
```

**Dependencias instaladas:**
- [x] fastapi==0.104.1
- [x] uvicorn[standard]==0.24.0
- [x] ollama==0.6.1
- [x] python-dotenv==1.0.0
- [x] pydantic==2.5.0
- [x] numpy>=1.24.0
- [x] scikit-learn>=1.3.0
- [x] sentence-transformers>=2.2.0
- [x] fuzzywuzzy[speedup]>=0.18.0

### 2.2 Verificar instalación

```bash
python -c "import numpy; import sklearn; print('✓ Dependencias OK')"
```

**Estado:** ☐ Completado

---

## ⚙️ Paso 3: Configurar Ollama

### 3.1 Instalar Ollama
- Descargar desde https://ollama.ai
- Ejecutar instalador
- Reiniciar máquina

### 3.2 Descargar Modelo

```bash
ollama pull qwen2.5:7b-instruct
```

**Notas:**
- Tamaño: ~4.7 GB
- Tiempo: 5-10 minutos (depende de internet)
- Alternativa compacta: `qwen2.5:3b-instruct` (~2.0 GB)

### 3.3 Verificar

```bash
ollama list
# Debe mostrar: qwen2.5:7b-instruct
```

**Estado:** ☐ Completado

---

## 🔧 Paso 4: Configurar Archivo `.env`

### 4.1 Crear archivo `.env`

En directorio raíz del proyecto: `c:\Users\huver\Desktop\IurisLex_Pro\.env`

```env
# Configuración Ollama
OLLAMA_HOST=http://127.0.0.1:11434
LLM_MODEL=qwen2.5:7b-instruct
OLLAMA_FALLBACK_MODEL=qwen2.5:3b-instruct

# Logging (Opcional)
LOG_LEVEL=INFO
```

### 4.2 Verificar Variables

```bash
# Verificar que .env existe
ls .env

# En Python
from dotenv import load_dotenv
load_dotenv()
import os
print(os.getenv('OLLAMA_HOST'))  # Debe imprimir URL
```

**Estado:** ☐ Completado

---

## ▶️ Paso 5: Iniciar Servicios

### 5.1 Terminal 1: Iniciar Ollama

```bash
ollama serve
# Resultado esperado: "Listening on 127.0.0.1:11434"
```

⏱️ **Deja corriendo permanentemente**

### 5.2 Terminal 2: Iniciar API

```bash
cd c:\Users\huver\Desktop\IurisLex_Pro
python -m uvicorn app.api.main:app --reload --host 127.0.0.1 --port 8000
```

**Resultado esperado:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
✓ Conectado a Ollama en http://127.0.0.1:11434
✓ Cargados 1091 artículos constitucionales
✓ Motor de búsqueda híbrido inicializado
```

**Estado:** ☐ Completado

---

## 🧪 Paso 6: Validar Instalación

### 6.1 Health Check

```bash
# Terminal 3: Test
curl http://localhost:8000/api/health

# Resultado:
{
  "status": "healthy",
  "articles_loaded": 1091,
  "ollama_connected": true,
  "search_engine_ready": true,
  "embeddings_available": true,
  "version": "2.0"
}
```

**Esperado:** Todos los campos `true` ✅

### 6.2 Test Básico

```bash
# Prueba simple de búsqueda
curl -X POST http://localhost:8000/api/consulta \
  -H "Content-Type: application/json" \
  -d '{"query": "¿Cuál es mi derecho a la igualdad?"}'

# Debe retornar JSON con artículo 13
```

### 6.3 Ejecutar Suite de Pruebas

```bash
python test_rag_v2.py
# Debe pasar todos los tests

python example_usage.py
# Debe ejecutar 8 ejemplos sin errores
```

**Estado:** ☐ Completado

---

## 🌐 Paso 7: Acceder a Interfaces

### 7.1 Interfaz Web

Abrir navegador: http://localhost:8000

**Debe ver:** Página principal de IurisLex con formulario de búsqueda

### 7.2 API Documentation (Swagger)

Ir a: http://localhost:8000/docs

**Debe ver:** Documentación interactiva de todos los endpoints
- POST /api/consulta
- POST /api/search-advanced
- POST /api/action-route
- GET /api/health
- etc.

### 7.3 Alternative Docs (ReDoc)

Ir a: http://localhost:8000/redoc

**Debe ver:** Documentación alternativa más legible

**Estado:** ☐ Completado

---

## 📊 Paso 8: Validación de Funcionalidades

### 8.1 Búsqueda Básica ✓

- [ ] Prueba: "¿Qué es la igualdad?"
- [ ] Resultado esperado: Art. 13
- [ ] Validación: confidence_score > 0.8

### 8.2 Búsqueda con Typo ✓

- [ ] Prueba: "dereccho al trabjo"
- [ ] Resultado esperado: Art. 25, 53 (incluso con typos)
- [ ] Validación: search_type = "hybrid"

### 8.3 Búsqueda Avanzada ✓

- [ ] Endpoint: POST /api/search-advanced
- [ ] Prueba: "derecho al trabajo"
- [ ] Resultado: Top-5 artículos con scores

### 8.4 Ruta de Acción ✓

- [ ] Endpoint: POST /api/action-route
- [ ] Prueba: "Fui despedida sin justificación"
- [ ] Resultado: Artículos + pasos + acciones disponibles

### 8.5 Artículo Específico ✓

- [ ] Endpoint: GET /api/articles/13
- [ ] Resultado: Artículo 13 completo

### 8.6 Listar Artículos ✓

- [ ] Endpoint: GET /api/articles?limit=5
- [ ] Resultado: Primeros 5 artículos

**Estado:** ☐ Todos completados

---

## 🚨 Paso 9: Troubleshooting

### Problema: "Error: Ollama no conecta"

**Checklist:**
- [ ] ¿Ollama está corriendo? (`ollama serve` en terminal)
- [ ] ¿Puerto es 11434? (Verificar en `.env`)
- [ ] ¿Firewall permite conexión?
- [ ] Solución: Reiniciar Ollama y API

**Verificación:**
```bash
curl http://127.0.0.1:11434/api/tags
# Si falla, problema en Ollama
```

### Problema: "No se encuentra modelo qwen"

**Checklist:**
- [ ] ¿Ejecutaste `ollama pull qwen2.5:7b-instruct`?
- [ ] ¿Completó descarga? (Verificar con `ollama list`)
- [ ] Solución: Descargar modelo nuevamente

### Problema: "Respuestas muy lentas"

**Opciones:**
- [ ] Usar modelo más pequeño: `qwen2.5:3b-instruct`
- [ ] Aumentar RAM disponible
- [ ] Reducir `top_k` en búsquedas

### Problema: "API retorna errores 500"

**Checklist:**
- [ ] Ver logs de la API (terminal)
- [ ] Ejecutar: `python test_rag_v2.py`
- [ ] Verificar que CSV existe en data/processed/

**Solución:**
```bash
# Reiniciar API
Ctrl+C en terminal
python -m uvicorn app.api.main:app --reload
```

---

## 📈 Paso 10: Optimización Post-Despliegue

### 10.1 Performance

- [ ] Monitorear tiempo de respuesta (objetivo: <3s)
- [ ] Si lento: Considerar caché Redis
- [ ] Usar curl para profiling:
  ```bash
  curl -w "Tiempo: %{time_total}s\n" http://localhost:8000/api/health
  ```

### 10.2 Escalabilidad

- [ ] Para múltiples usuarios: Usar Gunicorn
  ```bash
  pip install gunicorn
  gunicorn -w 4 -b 0.0.0.0:8000 app.api.main:app
  ```

- [ ] Para producción: Docker
  ```bash
  docker build -t iurislex:v2 .
  docker run -p 8000:8000 iurislex:v2
  ```

### 10.3 Monitoreo

- [ ] Configurar logging centralizado
- [ ] Setup de alertas
- [ ] Backup de datos periódico

---

## ✅ Paso 11: Validación Final

### Checklist Final

- [ ] Ollama corriendo
- [ ] API corriendo sin errores
- [ ] Health check: todos `true`
- [ ] Búsqueda básica funciona
- [ ] Búsqueda con typo funciona
- [ ] Ruta de acción funciona
- [ ] Tests pasan
- [ ] Documentación accesible
- [ ] Interfaz web carga
- [ ] API docs funciona

### Sign-Off

- [ ] **Desarrollador:** Validó funcionamiento
- [ ] **QA:** Ejecutó tests
- [ ] **Stakeholder:** Aprobó funcionalidades
- [ ] **Documentación:** Completa y actual

**Estado:** ☐ LISTO PARA PRODUCCIÓN ✅

---

## 📚 Documentación Requerida

- [x] RESUMEN_EJECUTIVO.md - Visión general
- [x] ARQUITECTURA_V2.md - Técnico detallado
- [x] QUICKSTART.md - Guía rápida
- [x] DIAGNOSTICO_Y_CORRECCIONES.md - Análisis de problemas
- [x] CHECKLIST_DESPLIEGUE.md - Este archivo
- [x] test_rag_v2.py - Suite de pruebas
- [x] example_usage.py - Ejemplos de uso

---

## 🎯 Próximos Pasos

### Inmediato (Semana 1)
- [ ] Desplegar en servidor de producción
- [ ] Configurar HTTPS
- [ ] Implementar autenticación (si es requerido)

### Corto Plazo (Semana 2-3)
- [ ] Implementar caché Redis
- [ ] Agregar monitoreo
- [ ] Fine-tuning con datos reales

### Mediano Plazo (Mes 1-2)
- [ ] Integración con Corte Constitucional
- [ ] Generación de documentos
- [ ] Multi-idioma

---

## 📞 Contacto y Soporte

**En caso de problemas:**
1. Consultar documentación (QUICKSTART.md)
2. Ejecutar tests (test_rag_v2.py)
3. Revisar logs del sistema
4. Contactar equipo de desarrollo

---

**Checklist completado:** ✅  
**Fecha:** Abril 2026  
**Estado:** LISTO PARA PRODUCCIÓN  
**Versión:** 2.0
