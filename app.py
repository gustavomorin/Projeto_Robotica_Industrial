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
        subprocess.run(cmd, check=True)
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


@app.route('/test_photo', methods=['POST'])
def test_photo():
    try:
        data = request.get_json() or {}
        formato_folha = data.get('formato', 'A4-p')
        largura_res = data.get('largura', 720)
        altura_res = data.get('altura', 794)

        env = os.environ.copy()
        env['FORMATO_FOLHA'] = formato_folha
        env['LARGURA_RES'] = str(largura_res)
        env['ALTURA_RES'] = str(altura_res)

        # Roda apenas o processamento de pontos
        subprocess.run([
            sys.executable, 'img_to_points6.py',
            os.path.join(UPLOAD_FOLDER, 'foto.png'),
            '--output', 'pontos_dither.csv'
        ], check=True, env=env)

        return jsonify(status='tested')
    except subprocess.CalledProcessError as e:
        return jsonify(status='error', message=str(e)), 500


@app.route('/process_photo', methods=['POST'])
def process_photo():
    try:
        data = request.get_json() or {}
        formato_folha = data.get('formato', 'A4-p')
        largura_res = data.get('largura', 720)
        altura_res = data.get('altura', 794)

        env = os.environ.copy()
        env['FORMATO_FOLHA'] = formato_folha
        env['LARGURA_RES'] = str(largura_res)
        env['ALTURA_RES'] = str(altura_res)

        # Gera CSV de pontos
        subprocess.run([
            sys.executable, 'img_to_points6.py',
            os.path.join(UPLOAD_FOLDER, 'foto.png'),
            '--output', 'pontos_dither.csv'
        ], check=True, env=env)

        # Envia pontos ao robô
        print("=== Iniciando envio de pontos (enviar_para_ur.py) ===")
        p = subprocess.Popen(
            [sys.executable, 'enviar_para_ur.py'],
            stdout=sys.stdout,
            stderr=sys.stderr,
            env=env
        )
        p.wait()

        return jsonify(status='done')
    except subprocess.CalledProcessError as e:
        return jsonify(status='error', message=str(e)), 500


if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
