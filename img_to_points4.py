from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import csv
from rembg import remove
import io
import subprocess

def assign_pen_color(rgb):
    pens = {
        'marrom':   np.array([150,  75,   0]),
        'preta':    np.array([  0,   0,   0]),
        'azul':     np.array([  0,   0, 255]),
        'vermelho': np.array([255,   0,   0]),
        'amarelo':  np.array([255, 255,   0]),
        'salmao':   np.array([250, 128, 114]),
    }
    color = np.array(rgb)
    best_pen = None
    min_dist = float('inf')
    for name, pen_rgb in pens.items():
        dist = np.linalg.norm(color - pen_rgb)
        if dist < min_dist:
            min_dist = dist
            best_pen = name
    return best_pen

def image_to_pointcloud(image_path, output_csv='points.csv', width=200, step=1, white_thresh=255):
    """
    Converte uma imagem em um conjunto de pontos coloridos com remoção de fundo e fundo branco aplicado.
    """

    print("[📷] Iniciando processamento da imagem...")

    # === 1. Remove fundo da imagem ===
    with open(image_path, 'rb') as f:
        input_bytes = f.read()
    output_bytes = remove(input_bytes)
    img_rgba = Image.open(io.BytesIO(output_bytes)).convert('RGBA')

    # === 2. Substitui fundo transparente por branco ===
    bg = Image.new("RGBA", img_rgba.size, (255, 255, 255, 255))
    img_com_fundo_branco = Image.alpha_composite(bg, img_rgba)
    img = img_com_fundo_branco.convert('RGB')

    # Salvar imagem para debug
    debug_path = 'img/fotopessoa_branco_debug.png'
    img.save(debug_path)
    print(f"[🖼️] Imagem com fundo branco salva como: {debug_path}")

    # === 3. Redimensiona imagem mantendo proporção ===
    w_pct = width / float(img.size[0])
    height = int(img.size[1] * w_pct)
    img = img.resize((width, height), resample=Image.LANCZOS)
    arr = np.array(img)

    # === 4. Gera coordenadas e cores ===
    ys, xs = np.indices((height, width))
    xs = xs.flatten()
    ys = ys.flatten()
    colors = arr.reshape(-1, 3)

    # === 5. Amostragem ===
    if step > 1:
        xs = xs[::step]
        ys = ys[::step]
        colors = colors[::step]

    # === 6. Filtra pixels não totalmente brancos
    mask = np.any(colors < white_thresh, axis=1)
    xs = xs[mask]
    ys = ys[mask]
    colors = colors[mask]

    print(f"[✔️] Total de pontos considerados: {len(xs)}")

    # === 7. Salva CSV ===
    with open(output_csv, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['x', 'y', 'r', 'g', 'b', 'pen'])
        for x, y, (r, g, b) in zip(xs, ys, colors):
            pen = assign_pen_color((r, g, b))
            writer.writerow([int(x), int(y), int(r), int(g), int(b), pen])

    print(f"[💾] CSV salvo em: {output_csv}")

    # === 8. Salva gráfico como imagem (em vez de mostrar)
    plt.figure(figsize=(8, 8))
    plt.scatter(xs, -ys, s=1, c=colors / 255.0)
    plt.axis('off')
    plt.title(f'Point Cloud (step={step}, white_thresh={white_thresh})')

    output_img = output_csv.replace('.csv', '_scatter.png')
    plt.savefig(output_img, bbox_inches='tight', dpi=300)
    plt.close()

    print(f"[🖼️] Imagem da nuvem de pontos salva como: {output_img}")

    # === 9. Executa script de envio automático para o robô
    print("[🔁] Executando script de envio para o robô (enviar_para_ur.py)...")
    try:
        resultado = subprocess.run(['python', 'enviar_para_ur.py'], check=True)
        print("[✅] Script de envio executado com sucesso.")
    except subprocess.CalledProcessError as e:
        print("[❌] Erro ao executar o script de envio.")
        print(e)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Gera nuvem de pontos coloridos e envia ao robô (UR).')
    parser.add_argument('image', help='Caminho para a imagem de entrada')
    parser.add_argument('--width', type=int, default=200, help='Largura alvo para amostragem')
    parser.add_argument('--step', type=int, default=1, help='Amostragem de pontos')
    parser.add_argument('--white_thresh', type=int, default=255, help='Remove pixels com r,g,b >= limiar')
    parser.add_argument('--output', default='points.csv', help='CSV de saída')
    args = parser.parse_args()
    image_to_pointcloud(
        args.image,
        output_csv=args.output,
        width=args.width,
        step=args.step,
        white_thresh=args.white_thresh
    )


# python img_to_points4.py img\fotopessoa4.png --width 300 --step 2 --white_thresh 230 --output pontos.csv




