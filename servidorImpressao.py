import socket
import threading
import time
from datetime import datetime

def ServidorImpressao():
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    servidor.bind(('localhost', 6000))
    servidor.listen()
    print("[Servidor de Impressão] Aguardando requisições em localhost:6000")

    while True:
        conexao, endereco = servidor.accept()
        threading.Thread(target=ProcessarImpressao, args=(conexao,)).start()

def ProcessarImpressao(conexao):
    try:
        dados = conexao.recv(1024).decode()
        if dados.startswith("{id:"):
            partes = dados.strip('{}').split(',')
            idRemetente = partes[0].split(':')[1].strip()
            numeroStr = dados.split('sequencia:')[1].strip().rstrip('}')
            numeros = eval(numeroStr)
            for numero in numeros:
                timestampImpressao = datetime.now().strftime("%H:%M:%S.%f")[:-3]
                print(f"[{timestampImpressao}] Processo {idRemetente} imprime {numero}")
    except Exception as e:
        print(f"[Impressora] Erro ao imprimir: {e}")
    finally:
        conexao.close()