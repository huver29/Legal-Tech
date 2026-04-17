# IurisLex: Mentor Constitucional

Consulta la Constitución Política de Colombia de 1991 con análisis jurídico en tiempo real, impulsado por modelos de lenguaje local (Ollama).

## Requisitos Previos

1. **Python 3.9+** instalado
2. **Ollama** instalado y corriendo localmente en `http://127.0.0.1:11434`
3. **Modelo descargado** en Ollama: `qwen2.5:7b-instruct`

### Instalar Ollama y descargar modelo

```bash
# Descargar Ollama desde https://ollama.ai

# En terminal separada, descargar el modelo:
ollama pull qwen2.5:7b-instruct

# Iniciar Ollama (si no está ya corriendo):
ollama serve
```

## Setup del Proyecto

### 1. Clonar/Descargar el Proyecto

```bash
cd c:\Users\huver\Desktop\IurisLex_Pro
```

### 2. Crear Entorno Virtual

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1  # En PowerShell
# O en cmd.exe:
# .venv\Scripts\activate.bat
```

### 3. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar Variables de Entorno (Opcional)

El archivo `.env` ya existe con valores por defecto:
```
PREFERRED_PROVIDER=ollama
LLM_MODEL=qwen2.5:7b-instruct
OLLAMA_HOST=http://127.0.0.1:11434
```

Si necesitas cambiar algo, edita `.env`.

## Ejecución

### Iniciar la Aplicación

```bash
python -m uvicorn app.api.main:app --reload --host 127.0.0.1 --port 8000
```

Salida esperada:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

### Abrir en el Navegador

```
http://127.0.0.1:8000/
```

## Endpoints Disponibles

### 1. **Interfaz Web (HTML)**
- **URL**: `GET http://127.0.0.1:8000/`
- **Descripción**: Interfaz gráfica profesional para consultar la Constitución

### 2. **Consulta Constitucional**
- **URL**: `POST http://127.0.0.1:8000/api/consulta`
- **Body**: `{"query": "artículo 1"}` o `{"query": "libertad"}`
- **Response**: JSON con artículo, análisis, comparación, caso y respuesta de IA

**Ejemplo:**
```bash
curl -X POST http://127.0.0.1:8000/api/consulta \
  -H "Content-Type: application/json" \
  -d '{"query": "libertad"}'
```

### 3. **Obtener Artículo por Número**
- **URL**: `GET http://127.0.0.1:8000/api/articles/1`
- **Response**: JSON con datos del artículo 1

### 4. **Documentación Interactiva**
- **Swagger UI**: `http://127.0.0.1:8000/docs`
- **ReDoc**: `http://127.0.0.1:8000/redoc`

## Estructura del Proyecto

```
IurisLex_Pro/
├── app/
│   └── api/
│       └── main.py              # API FastAPI principal
├── web/
│   ├── index.html               # Interfaz web
│   └── assets/                  # Estilos y scripts estáticos
├── data/
│   └── processed/
│       └── cp_co_1991.csv       # Base de datos constitucional (380 artículos)
├── scripts/
│   └── ollama_test.py           # Script para probar conexión Ollama
├── .env                         # Configuración de variables
├── .gitignore
├── requirements.txt             # Dependencias Python
└── README.md                    # Este archivo
```

## Cómo Usar la Aplicación

1. **Escribe una consulta** en el cuadro de búsqueda:
   - Por número: `"artículo 1"`, `"1"`
   - Por tema: `"libertad"`, `"derecho al trabajo"`, `"igualdad"`

2. **Presiona "Preguntar"** o Enter

3. **Visualiza los resultados en 4 pestañas:**
   - **Consulta**: Texto completo del artículo + análisis de IA
   - **Comparación**: Artículos relacionados en el mismo título/capítulo
   - **Simulación**: Caso práctico basado en el artículo
   - **Análisis**: Enfoque simple, técnico y reflexión jurídica

## Troubleshooting

### "No se encontró un artículo"
- **Causa**: Query no coincide con ningún artículo
- **Solución**: Intenta con términos más simples o números directos (1-380)

### "No se pudo conectar con Ollama"
- **Causa**: Ollama no está corriendo
- **Solución**: 
  ```bash
  ollama serve  # En terminal separada
  ```

### "Modelo no encontrado"
- **Causa**: El modelo `qwen2.5:7b-instruct` no está descargado
- **Solución**:
  ```bash
  ollama pull qwen2.5:7b-instruct
  ```

### Error de puerto 8000 en uso
- **Solución**: Usa otro puerto:
  ```bash
  python -m uvicorn app.api.main:app --host 127.0.0.1 --port 8001
  ```

### "ModuleNotFoundError: No module named 'fastapi'"
- **Solución**: Asegúrate de estar en el entorno virtual activado
  ```bash
  .venv\Scripts\Activate.ps1
  pip install -r requirements.txt
  ```

## Características Principales

✅ **Búsqueda Inteligente**: Encuentra artículos por número o contenido  
✅ **Análisis con IA**: Respuestas generadas por Ollama (local)  
✅ **Comparación de Artículos**: Identifica relaciones constitucionales  
✅ **Simulador de Casos**: Genera escenarios prácticos  
✅ **Análisis Múltiple**: Perspectiva simple, técnica y reflexiva  
✅ **Interfaz Profesional**: UI moderna y responsiva  
✅ **Sin conexión externa**: Todo corre localmente  

## Notas Técnicas

- **Base de datos**: 380 artículos + 59 artículos transitorios de la Constitución de 1991
- **LLM**: Ollama con modelo `qwen2.5:7b-instruct` (configurable)
- **Framework**: FastAPI + Uvicorn
- **Frontend**: HTML5 vanilla (sin frameworks pesados)
- **Codificación**: UTF-8

## Autor & Licencia

Proyecto: IurisLex Mentor Constitucional  
Datos: Constitución Política de Colombia de 1991  
Tecnología: FastAPI + Ollama

---

**¿Problemas?** Revisa los logs en la consola donde corre uvicorn o ejecuta:
```bash
python test_complete.py  # Test de búsqueda
python debug_search.py   # Debug de búsqueda específica
python scripts/ollama_test.py  # Test de conexión Ollama
```
