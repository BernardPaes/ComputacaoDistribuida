# main.py
import json
import threading
import time
from cliente import Cliente
from servidor import Servidor
from servidorImpressao import ServidorImpressao

def ObterTimestamp():
    return int(time.time() * 1000)

print("Computação Distribuída - Trabalho Prático - Exclusão Mútua")
numeroNos = int(input("Digite o número de nós a serem simulados: "))

configuracao = {}
portaBase = 5000
for i in range(numeroNos):
    configuracao[str(i)] = ("localhost", portaBase + i + 1)

threading.Thread(target=ServidorImpressao, daemon=True).start()

for i in range(numeroNos):
    cliente = Cliente(i, configuracao, ObterTimestamp)
    servidor = Servidor(i, configuracao, cliente)

    threading.Thread(target=servidor.IniciarServidor, daemon=True).start()
    threading.Thread(target=cliente.Executar, daemon=True).start()

input("\nPressione ENTER para encerrar o sistema...")