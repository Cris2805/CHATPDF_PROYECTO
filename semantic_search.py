#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
semantic_search.py  ·  Recupera los chunks más relevantes del libro
· Embeddings: text-embedding-3-large
· Ahora NO filtramos por threshold: siempre devolvemos los TOP-K ordenados
· Por defecto devolvemos K=5 resultados, pero en el app.py solo usaremos el primero.
"""

import os, json, numpy as np, faiss, openai
from pathlib import Path
from dotenv import load_dotenv

# ── Config ────────────────────────────────────────────────────────────
INDEX_PATH   = "embeddings.faiss"
META_PATH    = "meta.json"
EMBED_MODEL  = "text-embedding-3-large"
K_CANDIDATES = 5
# (ya no necesitamos THRESHOLD porque NO vamos a descartar hits)
# ───────────────────────────────────────────────────────────────────────

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
assert openai.api_key, "Falta OPENAI_API_KEY"

# 1) Carga índice y metadatos
index = faiss.read_index(INDEX_PATH)
meta  = json.loads(Path(META_PATH).read_text(encoding="utf-8"))

# 2) Helper: obtener embedding normalizado
def embed_text(text: str) -> np.ndarray:
    vec = openai.embeddings.create(
        input=text, model=EMBED_MODEL
    ).data[0].embedding
    vec = np.asarray(vec, dtype="float32")
    faiss.normalize_L2(vec.reshape(1, -1))
    return vec

# 3) Búsqueda principal (SIN umbral): siempre devolvemos los TOP-k más cercanos
def search(query: str, k: int = K_CANDIDATES):
    """
    Devuelve hasta k hits ordenados por similitud de coseno (de mayor a menor),
    con cada hit conteniendo: {score, id, text, page}.
    No filtramos por threshold: si no hay coincidencia fuerte, igual devolvemos el/top hit.
    """
    # 3.1) Obtenemos vector de consulta normalizado
    q_vec = embed_text(query).reshape(1, -1)
    # 3.2) Buscamos los k vectores más cercanos (en distancia L2 normalizado)
    D, I = index.search(q_vec, k)
    # 3.3) Convertimos distancias L2 normalizadas a puntajes de coseno
    cos_scores = 1 - (D[0] / 2)  # porque D = ||u-v||^2, con vectores normalizados
    results = []
    for s, idx in zip(cos_scores, I[0]):
        if idx == -1:
            continue
        item = meta[int(idx)]
        results.append({
            "score": float(s),
            "id":    int(idx),
            "text":  item["text"],
            "page":  item.get("page", -1)  # el campo “page” proveniente de chunks.json
        })
    # Ordenamos los resultados de mayor a menor similitud
    results.sort(key=lambda x: x["score"], reverse=True)
    return results

# 4) CLI de prueba rápida (opcional)
if __name__ == "__main__":
    print("Motor listo, devolviendo siempre el mejor hit.\n")
    while True:
        q = input("❓  ")
        if not q.strip():
            break

        hits = search(q, k=5)
        if not hits:
            print("🤖  No hay hits (¡esto no debería pasar!).\n")
        else:
            h = hits[0]
            print(f"→ (score={h['score']:.3f}, página={h['page']}) {h['text'][:200]}…\n")
