#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Genera embeddings con OpenAI (modelo text-embedding-3-large) para cada chunk
y construye un índice FAISS. Preserva el campo "page" que viene en chunks.json.
"""

import os, json, numpy as np, faiss
from pathlib import Path
from dotenv import load_dotenv
from tqdm import tqdm
import openai

# ---------- Configuración ----------
CHUNKS_PATH = Path("chunks.json")
INDEX_PATH  = Path("embeddings.faiss")
META_PATH   = Path("meta.json")

MODEL       = "text-embedding-3-large"
BATCH       = 50
# -----------------------------------

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
assert openai.api_key, "Falta OPENAI_API_KEY en el entorno"

# 1) Cargar chunks (ya contienen "id", "page", "text", "n_tokens")
chunks_raw = json.loads(CHUNKS_PATH.read_text(encoding="utf-8"))
texts = [c["text"] for c in chunks_raw]

# 2) Generar embeddings por lotes
def embed_batch(batch):
    resp = openai.embeddings.create(input=batch, model=MODEL)
    return [d.embedding for d in resp.data]

vectors = []
for i in tqdm(range(0, len(texts), BATCH), desc="🔄 Generando embeddings"):
    batch = texts[i : i + BATCH]
    vectors.extend(embed_batch(batch))

vectors = np.array(vectors, dtype="float32")
dims = vectors.shape[1]

# 3) Crear índice FAISS con vectores normalizados
faiss.normalize_L2(vectors)
index = faiss.IndexFlatL2(dims)
index.add(vectors)
faiss.write_index(index, str(INDEX_PATH))

# 4) Guardar meta.json (idéntico a chunks.json)
with META_PATH.open("w", encoding="utf-8") as f:
    json.dump(chunks_raw, f, ensure_ascii=False, indent=2)

# 5) Mensaje final
print("✅ Embeddings y metadatos listos:")
print(f"   → {INDEX_PATH}  ({index.ntotal} vectores)")
print(f"   → {META_PATH}")
