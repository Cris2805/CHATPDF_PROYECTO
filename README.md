
 CHATPDF_PROYECTO
Proyecto Flask + PDF.js con resaltado automático

CHATPDF_PROYECTO

Buscador del Libro de IA
Aplicación web (Flask + PDF.js) que permite a un usuario:

Hacer preguntas sobre el libro “Introducción a la Inteligencia Artificial: Una visión introductoria” (PDF).

Obtener respuestas basadas en fragmentos relevantes del texto.

Ver, en el visor PDF, el pasaje fuente resaltado y desplazarse automáticamente a la página correspondiente.

Mostrar un mensaje claro cuando no haya información disponible en el libro.

Estructura del Proyecto

CHATPDF_PROYECTO/
│
├── static/
│ ├── css/
│ │ └── styles.css ← Estilos generales (chat, PDF-header, etc.)
│ ├── js/
│ │ └── chat.js ← Lógica de frontend (AJAX a /ask, scroll/highlight)
│ ├── img/
│ │ ├── logo1.png ← Logo izquierda en cabecera del visor PDF
│ │ └── logo2.png ← Logo derecha en cabecera del visor PDF
│ ├── pdfs/
│ │ └── chatbot.pdf ← PDF del libro
│ └── pdfjs/ ← Copia completa de PDF.js (build + web)
│
├── templates/
│ └── index.html ← Página principal (dos paneles: PDF + Chat)
│
├── app.py ← Aplicación Flask (endpoints / y /ask)
├── extract_and_chunk.py ← Extrae texto del PDF y genera chunks.json
├── chunks.json ← Fragmentos (“chunks”) resultantes
├── meta.json ← Metadatos de cada chunk (página, tokens, etc.)
├── embed_and_index.py ← Genera embeddings y crea embeddings.faiss
├── embeddings.faiss ← Base FAISS de embeddings precomputados
├── semantic_search.py ← Búsqueda semántica (consulta FAISS + similitud)
├── qa_engine.py ← Lógica para construir respuestas con OpenAI
├── requirements.txt ← Dependencias Python (Flask, openai, faiss-cpu…)
├── README.md ← Este archivo
└── .gitignore ← Ignorar venv/, pycache/, .env, etc.

Requisitos Previos
Python 3.8+

pip (gestor de paquetes de Python)

(Opcional) Entorno virtual (venv, virtualenv, conda…)

Clave de API de OpenAI (exportada como OPENAI_API_KEY)

Internet (solo para llamar a OpenAI; la búsqueda local en FAISS no requiere red)

Instalación
Clonar el repositorio
git clone https://github.com/tu_usuario/CHATPDF_PROYECTO.git
cd CHATPDF_PROYECTO

Crear y activar un entorno virtual (recomendado)
– Linux/Mac:
python3 -m venv venv
source venv/bin/activate
– Windows (PowerShell):
python -m venv venv
.\venv\Scripts\Activate.ps1

Instalar dependencias
pip install -r requirements.txt

Configurar clave de OpenAI
Crear un archivo .env en la raíz del proyecto con el contenido:
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

(Reemplazar sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx por tu clave real)

Generar chunks y embeddings (opcional)
Si ya se incluyeron chunks.json y embeddings.faiss en el repositorio, pueden saltarse esta sección. Para regenerar desde cero:

Extraer y fragmentar el PDF
python extract_and_chunk.py
Esto genera chunks.json y meta.json (y opcional libro.txt).

Generar embeddings e indexar en FAISS
python embed_and_index.py
Esto crea embeddings.faiss.

Probar búsqueda semántica (opcional)
En la consola de Python:
from semantic_search import query_chunks
resultados = query_chunks("¿Qué es la inteligencia artificial?")
for r in resultados:
print(f"Página: {r['page']}, Score: {r['score']:.3f}")
print("Texto:", r["text"][:200], "...")

Ejecutar la aplicación Flask
En la raíz del proyecto y con el entorno virtual activado:
python app.py
(Por defecto se levanta en http://localhost:5000)

Abrir navegador
Navegar a http://localhost:5000

Verán:
– Panel izquierdo con el PDF embebido y dos logos en la cabecera.
– Panel derecho con el chat, botones sugeridos e historial de mensajes.

Pruebas y uso
Hacer clic en alguna de las preguntas sugeridas o escribir una propia.

Al enviar, el frontend hace POST a /ask con { "question": "…" }.

El backend consulta FAISS, genera respuesta (o mensaje de “no encontrado”).

El frontend muestra la respuesta y, si hay página, envía postMessage al PDF para scroll y highlight.

Ejemplos:
– Pregunta en el libro:
“¿Qué importancia tiene el álgebra booleana de George Boole en la IA?”
→ Resalta el fragmento y escribe la respuesta.
– Pregunta fuera del libro:
“¿Qué es la teoría de cuerdas?”
→ “Lo siento, no encontré información relevante sobre eso en el libro.”

Clonar y contribuir
git clone https://github.com/tu_usuario/CHATPDF_PROYECTO.git

cd CHATPDF_PROYECTO

python3 -m venv venv

source venv/bin/activate (o .\venv\Scripts\Activate.ps1 en Windows)

pip install -r requirements.txt

Crear .env con OPENAI_API_KEY

(Opcional) python extract_and_chunk.py && python embed_and_index.py

python app.py

Abrir http://localhost:5000

Créditos
Flask (web framework)

PDF.js (visor y highlight)

OpenAI (GPT-4/GPT-4o-mini) para generar respuestas

Sentence Transformers + FAISS (búsqueda de similitud semántica)

Licencia
Este proyecto está diseñado para fines educativos. Si deseas compartirlo públicamente, considera agregar una licencia MIT u otra apropiada.
>>>>>>> 7f261df (Versión inicial del proyecto ChatPDF)
