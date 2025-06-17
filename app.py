# app.py
from flask import Flask, render_template, request, jsonify
from qa_engine import answer
import semantic_search
import os
import traceback

app = Flask(__name__)
history = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def api_chat():
    data = request.get_json(force=True)
    pregunta = data.get('pregunta', '').strip()

    if not pregunta:
        return jsonify({
            'respuesta': 'No recibí ninguna pregunta.',
            'page': 1,
            'text': '',   # texto para resaltar (vacío por defecto)
            'bbox': None
        })

    try:
        # 1) Obtener respuesta de GPT
        respuesta_txt, new_history = answer(pregunta, history)
        history.clear()
        history.extend(new_history)

        # 2) Búsqueda semántica (siempre devolvemos al menos 1 hit)
        hits = semantic_search.search(pregunta, k=5)
        if hits and len(hits) > 0:
            mejor_chunk = hits[0]
            page_to_return = mejor_chunk.get("page", 1)
            text_to_highlight = mejor_chunk.get("text", "")
        else:
            # Fallback: página 1, sin texto
            page_to_return = 1
            text_to_highlight = ""
        
        return jsonify({
            'respuesta': respuesta_txt,
            'page': page_to_return,
            'text': text_to_highlight,
            'bbox': None
        })

    except Exception as e:
        traceback.print_exc()
        print("Error interno al procesar la petición:", e)
        return jsonify({
            'respuesta': 'Lo siento, ocurrió un error interno al procesar tu petición.',
            'page': 1,
            'text': '',
            'bbox': None
        })
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
