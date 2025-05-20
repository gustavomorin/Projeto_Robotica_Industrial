# img_to_points6.py

import os
import io
import csv
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
from rembg import remove

TARGET_RESOLUTION = (326, 277)  # largura × altura 626, 417 326, 277

def floyd_steinberg_dither(arr_gray, threshold):
    """
    Aplica Floyd–Steinberg com threshold customizável.
    Retorna máscara booleana onde True = pixel preto (a desenhar).
    """
    #arr = arr_gray.astype(float)
    # Aumenta brilho das regiões claras para remover ruídos
    arr = np.clip(arr_gray + 60, 0, 255)
    h, w = arr.shape
    for y in range(h):
        for x in range(w):
            old = arr[y, x]
            new = 0.0 if old < threshold else 255.0
            arr[y, x] = new
            err = old - new

            if x + 1 < w:
                arr[y, x + 1] += err * 7/16
            if y + 1 < h:
                if x > 0:
                    arr[y + 1, x - 1] += err * 3/16
                arr[y + 1, x]     += err * 5/16
                if x + 1 < w:
                    arr[y + 1, x + 1] += err * 1/16

    return (arr == 0)

def image_to_dither_pointcloud(image_path, output_csv='pontos_dither.csv',
                               threshold=128, max_points=10000):
    """
    Remove o fundo, redimensiona para 626×417, faz dithering e limita total de pontos.
    Gera:
     - pontos_dither.csv (x_pixel, y_pixel)
     - img/pontos_dither_debug.png (nuvem completa)
     - img/pontos_dither_debug_subsample.png (nuvem reduzida)
     - img/final_dither.png (subsample no tamanho 626×417)
    """
    print(f"[] Processando: {image_path}")
    print(f"[] Threshold = {threshold}, Max pontos = {max_points}")
    print(f"[] Redimensionando para {TARGET_RESOLUTION[0]}×{TARGET_RESOLUTION[1]}")

    # 1) Remove fundo
    with open(image_path, 'rb') as f:
        inp = f.read()
    out = remove(inp)
    img = Image.open(io.BytesIO(out)).convert('RGBA')

    # 2) Redimensiona para a resolução alvo
    img = img.resize(TARGET_RESOLUTION, resample=Image.LANCZOS)

    # 3) Composição sobre fundo branco + grayscale
    bg = Image.new("RGBA", img.size, (255,255,255,255))
    gray = Image.alpha_composite(bg, img).convert('L')
    arr_gray = np.array(gray, dtype=float)
    width, height = gray.size

    # 4) Dithering FS
    mask = floyd_steinberg_dither(arr_gray, threshold)
    ys, xs = np.nonzero(mask)
    total = len(xs)
    print(f"[] Total original: {total} pontos")

    # 5) Subamostragem para limitar número de pontos
    if max_points and total > max_points:
        idxs = np.random.choice(total, max_points, replace=False)
        xs = xs[idxs]; ys = ys[idxs]
        print(f"[] Subamostrado para {len(xs)} pontos")

    # 6) Salva CSV
    with open(output_csv, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['x_pixel','y_pixel'])
        for x, y in zip(xs, ys):
            writer.writerow([int(x), int(y)])
    print(f"[] CSV salvo em: {output_csv}")

    # 7) Gera debug PNGs no tamanho alvo
    os.makedirs('img', exist_ok=True)
    debug_full = np.where(mask, 0, 255).astype(np.uint8)
    Image.fromarray(debug_full, mode='L').save('img/pontos_dither_debug.png')
    subsample_mask = np.zeros_like(mask)
    subsample_mask[ys, xs] = True
    debug_sub = np.where(subsample_mask, 0, 255).astype(np.uint8)
    Image.fromarray(debug_sub, mode='L').save('img/pontos_dither_debug_subsample.png')
    print("[] Debug completo: img/pontos_dither_debug.png")
    print("[] Debug reduzido: img/pontos_dither_debug_subsample.png")

    # 8) Salva a visualização final no mesmo tamanho
    final_path = 'img/final_dither.png'
    Image.fromarray(debug_sub, mode='L').save(final_path)
    print(f"[] Final salvo em: {final_path}")

    # 9) Mostra na tela
    plt.figure(figsize=(width/100, height/100), dpi=100)
    plt.imshow(debug_sub, cmap='gray', origin='upper')
    plt.axis('off')
    plt.title(f'Dither FS (thr={threshold})')
    plt.show()

if __name__=='__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Dither FS em resolução fixa e limite de pontos.')
    parser.add_argument('image',      help='Caminho da imagem')
    parser.add_argument('--output',   default='pontos_dither.csv',  help='CSV de saída')
    parser.add_argument('--threshold',type=int, default=128,         help='Threshold [0–255]')
    parser.add_argument('--max_points',type=int, default=10000,      help='Máx pontos no CSV')
    args = parser.parse_args()

    image_to_dither_pointcloud(
        image_path = args.image,
        output_csv = args.output,
        threshold  = args.threshold,
        max_points = args.max_points
    )

# python img_to_points6.py img/fotopessoa10.jpeg --output pontos_dither.csv --threshold 180 --max_points 100000