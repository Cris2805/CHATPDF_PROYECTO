#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Extrae texto de chatbot.pdf y lo fragmenta en chunks, anotando la página real.
Ahora usamos la tokenización de GPT-4 en lugar de GPT-3.5 Turbo.
  • max_tokens = 120
  • overlap    = 20
Genera:
  libro.txt   — texto plano completo (UTF-8)
  chunks.json — lista de {"id", "page", "text", "n_tokens"} (UTF-8)
Uso:
  python extract_and_chunk.py chatbot.pdf
"""

import argparse, json, re
from pathlib import Path
import pdfplumber, tiktoken
from tqdm import tqdm

# ───── Configuración global ────────────────────────────────────────────
MAX_TOKENS = 120        # tokens por chunk
OVERLAP    = 20         # tokens que se solapan entre chunks
ENCODING   = "utf-8"    # fuerza UTF-8 al escribir
CLEAN_RE   = re.compile(r"\s+")

# Usamos la tokenización de GPT-4 en lugar de GPT-3.5 Turbo:
enc = tiktoken.encoding_for_model("gpt-4")
# ────────────────────────────────────────────────────────────────────────

def extract_per_page(pdf_path: Path) -> list[str]:
    """
    Devuelve una lista de textos, donde cada índice i corresponde al
    contenido (con espacios normalizados) de la página (i+1) del PDF.
    """
    textos_por_pagina = []
    with pdfplumber.open(pdf_path) as pdf:
        for pagina in tqdm(pdf.pages, desc="Extrayendo páginas"):
            texto_crudo = pagina.extract_text() or ""
            texto_norm = CLEAN_RE.sub(" ", texto_crudo).strip()
            textos_por_pagina.append(texto_norm)
    return textos_por_pagina

def split_chunks(text: str, max_tokens: int, overlap: int) -> list[str]:
    """
    Fragmenta el texto dado en chunks de, como máximo, max_tokens tokens,
    usando el mismo esquema de tokenización que emplea GPT-4, y solapando
    overlap tokens entre un chunk y el siguiente.
    Devuelve lista de strings (cada string = un chunk).
    """
    words, chunks, cur_words, cur_toks = text.split(), [], [], 0
    for w in words:
        wt = len(enc.encode(w + " "))
        if cur_toks + wt > max_tokens:
            chunks.append(" ".join(cur_words))
            # Retroceder 'overlap' palabras
            cur_words = cur_words[-overlap:]
            cur_toks  = sum(len(enc.encode(x + " ")) for x in cur_words)
        cur_words.append(w)
        cur_toks += wt
    if cur_words:
        chunks.append(" ".join(cur_words))
    return chunks

def main(pdf_path: str):
    pdf_path = Path(pdf_path)
    txt_out  = Path("libro.txt")
    json_out = Path("chunks.json")

    print("▶ Extrayendo texto por página…")
    paginas = extract_per_page(pdf_path)

    # Guardar texto completo (opcional)
    texto_completo = "\n".join(paginas)
    txt_out.write_text(texto_completo, encoding=ENCODING)
    print(f"  Texto completo → {txt_out}\n")

    print(f"▶ Dividiendo en chunks (≤ {MAX_TOKENS} tokens) página a página…")
    todos_los_chunks = []
    chunk_id = 0

    for p_idx, texto_pagina in enumerate(paginas):
        if not texto_pagina:
            continue

        lista_chunks = split_chunks(texto_pagina, MAX_TOKENS, OVERLAP)
        for c in lista_chunks:
            payload_chunk = {
                "id": chunk_id,
                "page": p_idx + 1,
                "text": c,
                "n_tokens": len(enc.encode(c))
            }
            todos_los_chunks.append(payload_chunk)
            chunk_id += 1

    # Guardar chunks.json con "page" incluido
    json_out.write_text(
        json.dumps(todos_los_chunks, ensure_ascii=False, indent=2),
        encoding=ENCODING
    )
    print(f"  {len(todos_los_chunks)} chunks guardados → {json_out}\n")
    print("✅ Proceso completo: libro.txt y chunks.json listos.")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf", help="Ruta al PDF (ej. chatbot.pdf)")
    args = ap.parse_args()
    main(args.pdf)
