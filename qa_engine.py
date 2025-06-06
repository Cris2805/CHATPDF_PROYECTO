# qa_engine.py  – versión corregida para no pasar “threshold”
import os
import openai
import semantic_search
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

SYSTEM_PROMPT = (
    "Eres un asistente que SOLO puede responder usando el contexto "
    "proporcionado. Si la respuesta no está en el contexto, responde "
    "exactamente: No encontrado en el libro.\n"
    "Cuando respondas, explica en 2–4 frases claras y completas."
)

def answer(question: str, history):
    # 1) Ejecutamos la búsqueda semántica (cada hit tiene 'id', 'page' y 'text').
    #    Ya no pasamos `threshold`, porque semantic_search.search fue modificado.
    hits = semantic_search.search(question, k=5)
    if not hits:
        # Si no hay hits (muy raro porque siempre devolvemos al menos uno), devolvemos sin referencias
        salida = {
            "respuesta": "Lo siento, no encontré información relevante sobre eso en el libro.",
            "referencias": []
        }
        return salida, history

    # 2) Construimos el contexto concatenando solo el texto de los hits
    context = "\n\n".join(h["text"] for h in hits)

    # 3) Preparamos los mensajes para el LLM (GPT-4o-mini)
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for q_prev, a_prev in history[-3:]:
        messages += [
            {"role": "user", "content": q_prev},
            {"role": "assistant", "content": a_prev},
        ]
    messages.append({
        "role": "user",
        "content": (
            f"Contexto:\n\"\"\"\n{context}\n\"\"\"\n\n"
            f"Pregunta: {question}"
        ),
    })

    # 4) Llamamos al modelo GPT-4o-mini
    resp = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0,
        max_tokens=300,
    )
    answer_txt = resp.choices[0].message.content.strip()

    # 5) Preparamos la lista de referencias con id, page y text
    referencias = []
    for h in hits:
        referencias.append({
            "id":   h.get("id", None),
            "page": h.get("page", None),
            "text": h.get("text", "")
        })

    # 6) Construimos la salida final como diccionario
    salida = {
        "respuesta":   answer_txt,
        "referencias": referencias
    }

    # 7) Actualizamos el historial (para contexto en la próxima iteración)
    nuevo_history = history + [(question, answer_txt)]
    return salida, nuevo_history
