import cv2
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import csv

def image_to_pointcloud_bw(image_path,
                            output_csv='points.csv',
                            width=200,
                            step=1,
                            threshold=128):
    """
    Converte uma imagem para B&W e gera nuvem de pontos pretos em fundo branco.

    - threshold: valor de limiar (0-255) para binarização.
    - step: amostragem de pontos.
    """
    # Carrega e converte para grayscale
    img = Image.open(image_path).convert('L')
    # Redimensiona
    w_pct = width / float(img.size[0])
    height = int(img.size[1] * w_pct)
    img = img.resize((width, height), resample=Image.LANCZOS)
    arr = np.array(img)

    # Binariza: 0=preto (foreground), 255=branco (background)
    bin_arr = np.where(arr < threshold, 0, 255).astype(np.uint8)

    # Gera coords de pixels pretos
    ys, xs = np.where(bin_arr == 0)
    # Amostragem
    ys = ys[::step]; xs = xs[::step]

    # Salva CSV
    with open(output_csv, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['type','x','y'])
        for x, y in zip(xs, ys):
            writer.writerow(['point', int(x), int(y)])

    # Plot
    plt.figure(figsize=(8,8), facecolor='white')
    ax = plt.gca()
    ax.set_facecolor('white')
    ax.imshow(bin_arr, cmap='gray')
    ax.scatter(xs, ys, s=1, c='black')
    ax.axis('off')
    plt.show()


def image_to_strokecloud_bw(image_path,
                             output_csv='strokes.csv',
                             width=200,
                             threshold=128):
    """
    Converte imagem para B&W e detecta segmentos horizontais pretos.

    Saída CSV: type, y, start_x, end_x
    """
    # Carrega e converte para grayscale
    img = Image.open(image_path).convert('L')
    w_pct = width / float(img.size[0])
    height = int(img.size[1] * w_pct)
    img = img.resize((width, height), resample=Image.LANCZOS)
    arr = np.array(img)

    # Binariza
    bin_arr = np.where(arr < threshold, 0, 255).astype(np.uint8)

    strokes = []
    for y in range(height):
        in_seg = False
        start_x = 0
        for x in range(width):
            if bin_arr[y, x] == 0:  # preto
                if not in_seg:
                    in_seg = True
                    start_x = x
            else:
                if in_seg:
                    strokes.append((y, start_x, x-1))
                    in_seg = False
        if in_seg:
            strokes.append((y, start_x, width-1))

    # Salva CSV
    with open(output_csv, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['type','y','start_x','end_x'])
        for y, sx, ex in strokes:
            if sx == ex:
                writer.writerow(['point', y, sx, ''])
            else:
                writer.writerow(['line', y, sx, ex])

    # Plot
    plt.figure(figsize=(8,8), facecolor='white')
    ax = plt.gca()
    ax.set_facecolor('white')
    ax.imshow(bin_arr, cmap='gray')
    for y, sx, ex in strokes:
        if sx == ex:
            ax.plot(sx, y, 'k.', markersize=2)
        else:
            ax.hlines(y, sx, ex, colors='black', linewidth=1)
    ax.axis('off')
    plt.show()

if __name__=='__main__':
    import argparse
    parser = argparse.ArgumentParser(
        description='Gera B&W point/stroke cloud de uma imagem.'
    )
    parser.add_argument('image', help='Caminho da imagem')
    parser.add_argument('--mode', choices=['points','strokes'], default='strokes')
    parser.add_argument('--width', type=int, default=200,
                        help='Largura alvo')
    parser.add_argument('--threshold', type=int, default=128,
                        help='Valor para limiar B&W')
    parser.add_argument('--step', type=int, default=1,
                        help='Amostragem para points')
    parser.add_argument('--output', default=None,
                        help='Arquivo CSV de saída')
    args = parser.parse_args()
    out = args.output or ('points.csv' if args.mode=='points' else 'strokes.csv')
    if args.mode=='points':
        image_to_pointcloud_bw(args.image, out, args.width, args.step, args.threshold)
    else:
        image_to_strokecloud_bw(args.image, out, args.width, args.threshold)

# python img_to_points3.py img\\fotopessoa5.png --mode strokes --width 300 --threshold 150 --output strokes_bw.csv