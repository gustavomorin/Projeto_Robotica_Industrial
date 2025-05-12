from flask import Flask, request
import os
import subprocess

app = Flask(__name__)

UPLOAD_FOLDER = os.path.join(os.getcwd(), "img")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['image']
    path = os.path.join(UPLOAD_FOLDER, 'fotopessoa.png')
    file.save(path)
    print(f"[📷] Imagem recebida e salva em: {path}")

    try:
        subprocess.run(['python', 'img_to_points4.py', path, '--width', '300', '--step', '2', '--white_thresh', '230', '--output', 'pontos.csv'], check=True)
        return '[✅] Imagem processada e comandos enviados ao robô.', 200
    except Exception as e:
        print("[❌] Erro durante o processamento:", e)
        return '[❌] Erro ao processar a imagem.', 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
