# teste.py

from PIL import Image
import argparse

def main():
    parser = argparse.ArgumentParser(description='Verifica a resolução de uma imagem.')
    parser.add_argument('imagem', help='Caminho para o arquivo de imagem')
    args = parser.parse_args()

    try:
        img = Image.open(args.imagem)
        largura, altura = img.size
        print(f"Resolução de «{args.imagem}»: {largura}×{altura} pixels")
    except FileNotFoundError:
        print(f"Arquivo não encontrado: {args.imagem}")
    except Exception as e:
        print(f"Erro ao abrir a imagem: {e}")

if __name__ == '__main__':
    main()
