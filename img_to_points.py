import cv2
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import csv

def image_to_pointcloud(image_path,
                         output_csv='points.csv',
                         width=200,
                         edge_step=1,
                         low_thresh=50,
                         high_thresh=150,
                         interior_step=0):
    """
    Converte uma imagem em nuvem de pontos combinando bordas e interior.

    Parâmetros:
    - image_path: caminho para a imagem de entrada.
    - output_csv: nome do CSV de saída.
    - width: largura alvo para redimensionamento (mantém proporção).
    - edge_step: amostragem de pontos de borda; pega cada N-ésimo ponto de borda.
    - low_thresh/high_thresh: thresholds para detector Canny.
    - interior_step: se >0, amostra interior da pessoa a cada N pixels.
    """
    # 1. Carrega imagem e redimensiona
    img = Image.open(image_path).convert('RGB')
    w_pct = width / float(img.size[0])
    height = int(float(img.size[1]) * w_pct)
    img = img.resize((width, height), resample=Image.LANCZOS)
    arr = np.array(img)

    # 2. Detecta bordas
    gray = cv2.cvtColor(arr, cv2.COLOR_RGB2GRAY)
    edges = cv2.Canny(gray, low_thresh, high_thresh)
    ys_e, xs_e = np.where(edges > 0)
    cols_e = arr[ys_e, xs_e]

    # 3. Amostra bordas
    if edge_step > 1:
        ys_e = ys_e[::edge_step]
        xs_e = xs_e[::edge_step]
        cols_e = cols_e[::edge_step]

    # 4. Opcional: amostragem interior
    ys_i, xs_i, cols_i = np.array([], dtype=int), np.array([], dtype=int), np.empty((0,3), dtype=int)
    if interior_step > 0:
        # interior mask: não borda e não fundo branco
        mask_int = (edges == 0) & np.any(arr < 255, axis=2)
        ys_all, xs_all = np.where(mask_int)
        cols_all = arr[ys_all, xs_all]
        # amostragem interior
        ys_i = ys_all[::interior_step]
        xs_i = xs_all[::interior_step]
        cols_i = cols_all[::interior_step]

    # 5. Combina bordas e interior
    xs = np.concatenate([xs_e, xs_i])
    ys = np.concatenate([ys_e, ys_i])
    colors = np.vstack([cols_e, cols_i])

    # 6. Salva CSV
    with open(output_csv, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['x', 'y', 'r', 'g', 'b'])
        for x, y, (r, g, b) in zip(xs, ys, colors):
            writer.writerow([int(x), int(y), int(r), int(g), int(b)])

    # 7. Plota
    plt.figure(figsize=(8, 8))
    plt.scatter(xs, -ys, s=1, c=colors / 255.0)
    plt.axis('off')
    plt.title(f'Edge+Interior PointCloud (edge_step={edge_step}, interior_step={interior_step})')
    plt.show()

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(
        description='Gera nuvem de pontos de borda e interior reduzido.'
    )
    parser.add_argument('image', help='Caminho para a imagem de entrada')
    parser.add_argument('--width', type=int, default=200,
                        help='Largura alvo para redimensionamento')
    parser.add_argument('--edge_step', type=int, default=1,
                        help='Amostragem de bordas: cada N-ésimo ponto')
    parser.add_argument('--low_thresh', type=int, default=50,
                        help='Lower threshold para Canny')
    parser.add_argument('--high_thresh', type=int, default=150,
                        help='Higher threshold para Canny')
    parser.add_argument('--interior_step', type=int, default=0,
                        help='Amostragem interior: cada N-ésimo ponto')
    parser.add_argument('--output', default='points.csv',
                        help='Arquivo CSV de saída')
    args = parser.parse_args()
    image_to_pointcloud(
        args.image,
        output_csv=args.output,
        width=args.width,
        edge_step=args.edge_step,
        low_thresh=args.low_thresh,
        high_thresh=args.high_thresh,
        interior_step=args.interior_step
    )

# Exemplo de uso:
# python img_to_points.py img\fotopessoa4.png --width 300 --edge_step 2 --low_thresh 20 --high_thresh 230 --interior_step 10 --output pontos_mix.csv
