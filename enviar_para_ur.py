'''import socket
import time
import pandas as pd

print('Program Started')

HOST = '10.103.16.162'  # IP do seu computador
PORT = 30000
CSV_PATH = 'pontos_dither.csv'
CHUNK_SIZE = 20

# Lê o CSV e extrai os valores da coluna 'x' como float
df = pd.read_csv(CSV_PATH)
valores_x = df['x_pixel'].tolist()
valores_y = df['y_pixel'].tolist()
total = len(valores_x)

# Envia blocos de 20 valores por vez
for i in range(0, total, CHUNK_SIZE):
    bloco = valores_x[i:i + CHUNK_SIZE]

    print('Aguardando conexão...')
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen(1)
    c, addr = s.accept()
    print(f'Conectado por {addr}')

    try:
        # Primeira mensagem deve ser "connected"
        recebida = c.recv(1024).decode('utf-8')
        print(f"[Robô disse - connected] (repr): {repr(recebida)}")

        if recebida.strip() != 'connected':
            print(f"[!] Esperado 'connected', mas recebido: '{recebida.strip()}'")
            c.close()
            s.close()
            continue
        else:
            print("[✓] Robô confirmou conexão.")

        # Agora envia os dados do bloco
        for idx, x in enumerate(bloco):
            solicitacao = c.recv(1024).decode('utf-8')
            print(f"[Robô disse - asking] (repr): {repr(solicitacao)}")
            if solicitacao.strip() == 'asking_for_data':
                #x_float = float(x)
                x = str(x)
                mensagem = f'({x})'.format(x)
                #print(f'[→] Enviando ponto {i + idx + 1}/{total}: {mensagem.strip()}')
                print(x)
                #c.send(mensagem.encode('utf-8'))
                c.send(mensagem.encode('utf-8'))
                time.sleep(30)
            else:
                print(f"[!] Mensagem inesperada: '{solicitacao.strip()}'")

    except socket.error as e:
        print(f'Erro de socket: {e}')

    c.close()
    s.close()

print('Finalizado.')'''

import socket
import time
import pandas as pd
from img_to_points6 import largura, altura

print('Program Started')

HOST = '10.103.16.162'  # IP do seu computador
PORT = 30000
CSV_PATH = 'pontos_dither.csv'
CHUNK_SIZE = 20  # Total de valores (10 x, 10 y)

# Tamanho da imagem original em pixels
#LARGURA_IMAGEM_PX = 326
#ALTURA_IMAGEM_PX = 277
LARGURA_IMAGEM_PX = largura
ALTURA_IMAGEM_PX = altura

# Tamanho da folha A4 em metros
LARGURA_FOLHA = 0.210
ALTURA_FOLHA = 0.297

# Lê o CSV
df = pd.read_csv(CSV_PATH)

# Fator de escala uniforme
escala_x = LARGURA_FOLHA / LARGURA_IMAGEM_PX
escala_y = ALTURA_FOLHA / ALTURA_IMAGEM_PX
escala = min(escala_x, escala_y)

# Conversão para metros
df['x_m'] = df['x_pixel'] * escala
df['y_m'] = df['y_pixel'] * escala

# Centralização do desenho na folha
largura_em_m = LARGURA_IMAGEM_PX * escala
altura_em_m = ALTURA_IMAGEM_PX * escala
offset_x = (LARGURA_FOLHA - largura_em_m) / 2
offset_y = (ALTURA_FOLHA - altura_em_m) / 2
df['x_m'] += offset_x
df['y_m'] += offset_y

valores_x = df['x_m'].tolist()
valores_y = df['y_m'].tolist()
total = len(valores_x)

# Envia blocos de 10 pares por vez
for i in range(0, total, CHUNK_SIZE // 2):
    bloco_x = valores_x[i:i + CHUNK_SIZE // 2]
    bloco_y = valores_y[i:i + CHUNK_SIZE // 2]

    # Se for o último bloco e tiver menos de 10 pontos, preenche com o último ponto
    '''if i + (CHUNK_SIZE // 2) >= total:
        while len(bloco_x) < 10:
            bloco_x.append(bloco_x[-1])
            bloco_y.append(bloco_y[-1])'''
    # Se for o último bloco e tiver menos de 10 pontos, preenche com 1
    if i + (CHUNK_SIZE // 2) >= total:
        while len(bloco_x) < 10:
            bloco_x.append(1)
            bloco_y.append(1)

    print('Aguardando conexão...')
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen(1)
    c, addr = s.accept()
    print(f'Conectado por {addr}')

    try:
        recebida = c.recv(1024).decode('utf-8')
        print(f"[Robô disse - connected] (repr): {repr(recebida)}")

        if recebida.strip() != 'connected':
            print(f"[] Esperado 'connected', mas recebido: '{recebida.strip()}'")
            c.close()
            s.close()
            continue
        else:
            print("[] Robô confirmou conexão.")

        solicitacao = c.recv(1024).decode('utf-8')
        print(f"[Robô disse - asking] (repr): {repr(solicitacao)}")

        if solicitacao.strip() == 'asking_for_data':
            lista_formatada = [f"{x:.5f}" for x in bloco_x] + [f"{y:.5f}" for y in bloco_y]
            mensagem = f"({','.join(lista_formatada)})"
            c.send(mensagem.encode('utf-8'))

            print(f'[] Enviando bloco {i//(CHUNK_SIZE//2) + 1} com {len(bloco_x)} pares:')
            print(f'  {mensagem}')

            # Aguarda confirmação de que o bloco foi processado
            confirmacao = c.recv(1024).decode('utf-8')
            print(f"[Robô disse - confirmação] (repr): {repr(confirmacao)}")
            if confirmacao.strip() != 'block_done':
                print("[] Esperado 'block_done', mas recebido algo diferente.")

            time.sleep(0.1)

        else:
            print(f"[] Mensagem inesperada: '{solicitacao.strip()}'")

    except socket.error as e:
        print(f'Erro de socket: {e}')

    c.close()
    s.close()

print('Finalizado.')