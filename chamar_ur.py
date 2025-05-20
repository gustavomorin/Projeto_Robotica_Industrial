# chamar_ur.py

import socket
import sys
import time

# IP e porta que o UR deve conectar
HOST = '10.103.16.162'
PORT = 30000

def main():
    if len(sys.argv) != 2:
        print(f"Uso: python {sys.argv[0]} <altura_cm>")
        sys.exit(1)

    altura = sys.argv[1]
    try:
        altura_val = float(altura)
    except ValueError:
        print("Erro: altura inválida. Deve ser um número.")
        sys.exit(1)

    print("=== Chamar UR Script ===")
    print(f"Aguardando conexão em {HOST}:{PORT} ...")

    # 1) Cria socket servidor
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen(1)

    # 2) Aceita conexão do UR
    conn, addr = s.accept()
    print(f"Conectado por {addr}")

    try:
        # 3) Espera handshake "connected"
        recebido = conn.recv(1024).decode('utf-8')
        print(f"[UR disse - connected] (repr): {repr(recebido)}")

        if recebido.strip() != 'connected':
            print(f"[ERROR] Esperado 'connected', mas recebeu: '{recebido.strip()}'")
            conn.close()
            s.close()
            sys.exit(1)
        else:
            print("[OK] Robô confirmou conexão.")

        # 4) UR pede dados
        solicitacao = conn.recv(1024).decode('utf-8')
        print(f"[UR disse - asking_for_data] (repr): {repr(solicitacao)}")

        if solicitacao.strip() == 'asking_for_data':
            mensagem = f"({altura_val:.2f})"
            conn.send(mensagem.encode('utf-8'))
            print(f"Enviado altura: {mensagem}")
            time.sleep(0.1)
        else:
            print(f"[ERROR] Mensagem inesperada: '{solicitacao.strip()}'")
            conn.close()
            s.close()
            sys.exit(1)

        # 5) Aguarda confirmação "posicionado"
        resp = conn.recv(1024).decode('utf-8').strip()
        print(f"[UR disse - posicionado] {resp!r}")
        if resp != 'posicionado':
            print(f"[ERROR] Esperado 'posicionado', mas recebeu: {resp!r}")
            conn.close()
            s.close()
            sys.exit(1)
        print("[OK] Robô posicionado com sucesso")

    except socket.error as e:
        print(f"Erro de socket: {e}")
    finally:
        # 6) Fecha conexões
        conn.close()
        s.close()
        print("=== Script Concluído ===")

if __name__ == "__main__":
    main()
