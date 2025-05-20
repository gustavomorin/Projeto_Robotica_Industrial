# app.py

import os
import sys
import subprocess
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

app = Flask(
    __name__,
    template_folder='src',
    static_folder='src',
    static_url_path=''
)
CORS(app)

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
IMG_FOLDER    = os.path.join(os.getcwd(), 'img')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(IMG_FOLDER, exist_ok=True)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/start_robot', methods=['POST'])
def start_robot():
    data = request.get_json() or {}
    altura = data.get('height')
    if altura is None:
        return jsonify(status='error', message='Altura não fornecida'), 400

    cmd = [sys.executable, 'chamar_ur.py', str(altura)]
    try:
        subprocess.run(cmd, check=True)  # herda stdout/err automaticamente
        return jsonify(status='posicionado')
    except subprocess.CalledProcessError as e:
        return jsonify(status='error', message=str(e)), 500


@app.route('/capture_photo', methods=['POST'])
def capture_photo():
    file = request.files.get('image')
    if not file:
        return jsonify(status='error', message='Imagem não enviada'), 400
    path = os.path.join(UPLOAD_FOLDER, 'foto.png')
    file.save(path)
    print(f"[📷] Foto salva em: {path}")
    return jsonify(status='received')


@app.route('/process_photo', methods=['POST'])
def process_photo():
    try:
        # 1) Gera o CSV de pontos
        subprocess.run([
            sys.executable, 'img_to_points6.py',
            os.path.join(UPLOAD_FOLDER, 'foto.png'),
            '--output', 'pontos_dither.csv'
        ], check=True)

        # 2) Envia os pontos ao robô com streaming de saída
        print("=== Iniciando envio de pontos (enviar_para_ur.py) ===")
        p = subprocess.Popen(
            [sys.executable, 'enviar_para_ur.py'],
            stdout=sys.stdout,
            stderr=sys.stderr
        )
        p.wait()  # aguarda terminar; tudo que enviar_para_ur.py imprimir aparecerá no seu terminal

        return jsonify(status='done')
    except subprocess.CalledProcessError as e:
        return jsonify(status='error', message=str(e)), 500


if __name__ == '__main__':
    # desliga o reloader pra não reiniciar no meio do envio
    app.run(debug=True, use_reloader=False)
