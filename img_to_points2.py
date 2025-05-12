import cv2
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import csv

def mask_by_largest_contour(pil_img: Image.Image) -> Image.Image:
    """
    Detecta o maior contorno da pessoa invertendo o threshold e pinta tudo fora dele de branco.

    Parâmetros:
    - pil_img: imagem PIL em RGB.
    Retorna:
    - PIL.Image com fundo branco fora do maior contorno.
    """
    arr = np.array(pil_img)
    gray = cv2.cvtColor(arr, cv2.COLOR_RGB2GRAY)
    # Inverte threshold para destacar a pessoa
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return pil_img
    largest = max(contours, key=cv2.contourArea)
    mask = np.zeros_like(gray)
    cv2.drawContours(mask, [largest], -1, color=255, thickness=-1)
    arr[mask == 0] = [255, 255, 255]
    return Image.fromarray(arr)


def image_to_pointcloud(image_path, output_csv='points.csv', width=200, step=1, white_thresh=255):
    """
    Converte uma imagem em nuvem de pontos, mantendo apenas a pessoa.
    Plota lado a lado: contorno da pessoa, imagem mascarada e nuvem de pontos.

    Parâmetros:
    - image_path: caminho para a imagem de entrada.
    - output_csv: nome do CSV a ser salvo.
    - width: largura alvo (mantém proporção).
    - step: amostragem, use cada N-ésimo ponto.
    - white_thresh: limiar acima do qual pixel é branco.
    """
    # Carrega e redimensiona
    img = Image.open(image_path).convert('RGB')
    w_percent = width / float(img.size[0])
    height = int(float(img.size[1]) * w_percent)
    img = img.resize((width, height), resample=Image.LANCZOS)

    # Prepara overlay com contorno da pessoa
    arr_img = np.array(img)
    gray = cv2.cvtColor(arr_img, cv2.COLOR_RGB2GRAY)
    _, thresh_overlay = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    contours, _ = cv2.findContours(thresh_overlay, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        largest = max(contours, key=cv2.contourArea)
        overlay_arr = arr_img.copy()
        cv2.drawContours(overlay_arr, [largest], -1, (255, 0, 0), thickness=2)
        contour_img = Image.fromarray(overlay_arr)
    else:
        contour_img = img

    # Mascara tudo fora da pessoa
    masked_img = mask_by_largest_contour(img)
    arr_masked = np.array(masked_img)

    # Gera pontos
    ys, xs = np.indices((height, width))
    xs = xs.flatten()
    ys = ys.flatten()
    colors = arr_masked.reshape(-1, 3)

    if step > 1:
        xs = xs[::step]
        ys = ys[::step]
        colors = colors[::step]

    mask = np.any(colors < white_thresh, axis=1)
    xs, ys, colors = xs[mask], ys[mask], colors[mask]

    # Salva CSV
    with open(output_csv, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['x', 'y', 'r', 'g', 'b'])
        for x, y, (r, g, b) in zip(xs, ys, colors):
            writer.writerow([int(x), int(y), int(r), int(g), int(b)])

    # Plot dos três estágios
    fig, axs = plt.subplots(1, 3, figsize=(18, 8))
    axs[0].imshow(contour_img)
    axs[0].axis('off')
    axs[0].set_title('Contorno da Pessoa')
    axs[1].imshow(masked_img)
    axs[1].axis('off')
    axs[1].set_title('Imagem Mascarada')
    axs[2].scatter(xs, -ys, s=1, c=colors / 255.0)
    axs[2].axis('off')
    axs[2].set_title(f'Nuvem de Pontos (step={step})')
    plt.show()

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(
        description='Gera nuvem de pontos, mantendo só o maior contorno (pessoa).')
    parser.add_argument('image', help='Caminho para a imagem de entrada')
    parser.add_argument('--width', type=int, default=200, help='Largura alvo para amostragem')
    parser.add_argument('--step', type=int, default=1, help='Use cada N-ésimo ponto')
    parser.add_argument('--white_thresh', type=int, default=255, help='Limiar para remover brancos')
    parser.add_argument('--output', default='points.csv', help='Arquivo CSV de saída')
    args = parser.parse_args()
    image_to_pointcloud(
        args.image,
        output_csv=args.output,
        width=args.width,
        step=args.step,
        white_thresh=args.white_thresh
    )

    # python img_to_points2.py img\\fotopessoa7.png --width 300 --step 1 --white_thresh 250 --output pontos.csv