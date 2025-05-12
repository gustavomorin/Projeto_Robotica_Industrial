import cv2
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import csv

def image_to_pointcloud(image_path, output_csv='points.csv', width=200, step=1,
                         dark_thresh=128):
    """
    Converte uma imagem em nuvem de pontos em preto e branco,
    plotando apenas pixels suficientemente escuros.

    Parâmetros:
    - image_path: caminho para a imagem de entrada.
    - output_csv: CSV de saída.
    - width: largura alvo (mantém proporção).
    - step: amostragem de pontos; usa cada N-ésimo pixel.
    - dark_thresh: limiar (0-255); somente pixels com valor <= limiar são plotados.
    """
    # Carrega e converte para grayscale
    img_gray = Image.open(image_path).convert('L')
    # Redimensiona mantendo proporção
    w_pct = width / float(img_gray.size[0])
    height = int(float(img_gray.size[1]) * w_pct)
    img_gray = img_gray.resize((width, height), resample=Image.LANCZOS)
    arr = np.array(img_gray)

    # Gera coordenadas e valores de intensidade
    ys, xs = np.indices((height, width))
    xs = xs.flatten()
    ys = ys.flatten()
    vals = arr.flatten()

    # Aplica amostragem
    if step > 1:
        xs = xs[::step]
        ys = ys[::step]
        vals = vals[::step]

    # Filtra apenas pixels escuros (<= dark_thresh)
    mask = vals <= dark_thresh
    xs = xs[mask]
    ys = ys[mask]

    # Salva CSV
    with open(output_csv, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['type','x','y'])
        for x, y in zip(xs, ys):
            writer.writerow(['point', int(x), int(y)])

    # Plot preto e branco
    plt.figure(figsize=(8,8), facecolor='white')
    ax = plt.gca()
    ax.set_facecolor('white')
    ax.scatter(xs, -ys, s=1, color='black')
    plt.axis('off')
    plt.title(f'Point Cloud B&W (step={step}, dark_thresh={dark_thresh})', color='black')
    plt.show()

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(
        description='Gera nuvem de pontos B&W de uma imagem, plotando só pixels escuros.'
    )
    parser.add_argument('image', help='Caminho da imagem de entrada')
    parser.add_argument('--width', type=int, default=200, help='Largura alvo')
    parser.add_argument('--step', type=int, default=1, help='Amostragem de pontos')
    parser.add_argument('--dark_thresh', type=int, default=128,
                        help='Limiar: só pixels <= limiar serão plotados')
    parser.add_argument('--output', default='points.csv', help='Arquivo CSV de saída')
    args = parser.parse_args()
    image_to_pointcloud(
        args.image,
        output_csv=args.output,
        width=args.width,
        step=args.step,
        dark_thresh=args.dark_thresh
    )

# python img_to_points5.py img\\fotopessoa4.png --width 300 --step 2 --dark_thresh 100 --output pontos_bw.csv
