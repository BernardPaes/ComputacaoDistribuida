import socket
import threading
import time
import random

RELEASED = 0
WANTED = 1
HELD = 2

class Cliente:
    def __init__(self, MeuId, Configuracao, ObterTimestamp):
        self.MeuId = MeuId
        self.Configuracao = Configuracao
        self.ObterTimestamp = ObterTimestamp
        self.TodosOsNos = list(Configuracao.keys())
        self.Estado = RELEASED
        self.TimestampAtual = 0
        self.TimestampUltimaMensagem = 0
        self.ConfirmacoesRecebidas = 0
        self.RespostasPostergadas = []
        self.Trava = threading.Lock()
        self.EnderecoServidorImpressao = ("localhost", 6000)

    def EnviarMensagem(self, DestinatarioId, Mensagem):
        host, porta = self.Configuracao[str(DestinatarioId)]
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect((host, porta))
                sock.sendall(Mensagem.encode())
        except Exception as e:
            print(f"[Erro] Falha ao enviar mensagem para {DestinatarioId}: {e}")

    def EnviarParaServidorImpressao(self, numeros):
        mensagem = f"{{id: {self.MeuId}, sequencia: {numeros}}}"
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect(self.EnderecoServidorImpressao)
                sock.sendall(mensagem.encode())
        except Exception as e:
            print(f"[Erro] Falha ao enviar para o servidor de impressão: {e}")

    def SolicitarSecaoCritica(self):
        with self.Trava:
            self.Estado = WANTED
            self.TimestampAtual = self.ObterTimestamp()
            self.ConfirmacoesRecebidas = 0
            self.TimestampUltimaMensagem = self.TimestampAtual
        print(f"[Cliente {self.MeuId}] Solicitando acesso com timestamp {self.TimestampAtual}")

        mensagem = f"{{{self.TimestampAtual}, {self.MeuId}}}"
        for Id in self.TodosOsNos:
            if int(Id) != self.MeuId:
                self.EnviarMensagem(int(Id), mensagem)

    def EntrarNaSecaoCritica(self):
        with self.Trava:
            self.Estado = HELD
        print(f"[Cliente {self.MeuId}] >>> Entrou na seção crítica")
        k = random.randint(1, 10)
        valorAtual = self.TimestampUltimaMensagem
        for i in range(k):
            numero = valorAtual + i
            self.EnviarParaServidorImpressao([numero])
            time.sleep(0.5)

    def LiberarSecaoCritica(self):
        with self.Trava:
            self.Estado = RELEASED
            for destinatario in self.RespostasPostergadas:
                resposta = f"{{ok, {self.MeuId}}}"
                self.EnviarMensagem(destinatario, resposta)
            self.RespostasPostergadas.clear()
        print(f"[Cliente {self.MeuId}] <<< Liberou a seção crítica")

    def ReceberOk(self):
        with self.Trava:
            self.ConfirmacoesRecebidas += 1

    def ReceberRequisicao(self, msg):
        try:
            partes = msg.strip('{}').split(',')
            timestampRemetente = int(partes[0].strip())
            remetenteId = int(partes[1].strip())
        except:
            print(f"[Cliente {self.MeuId}] Erro ao interpretar mensagem: {msg}")
            return

        with self.Trava:
            self.TimestampUltimaMensagem = max(self.TimestampUltimaMensagem, timestampRemetente)
            prioridadeRemetente = (timestampRemetente, remetenteId)
            prioridadeAtual = (self.TimestampAtual, self.MeuId)

            if self.Estado == HELD or (self.Estado == WANTED and prioridadeRemetente > prioridadeAtual):
                self.RespostasPostergadas.append(remetenteId)
            else:
                resposta = f"{{ok, {self.MeuId}}}"
                self.EnviarMensagem(remetenteId, resposta)

    def Executar(self):
        while True:
            time.sleep(2)
            if random.random() > 0.5:
                self.SolicitarSecaoCritica()
                while True:
                    with self.Trava:
                        if self.ConfirmacoesRecebidas >= len(self.TodosOsNos) - 1:
                            break
                    time.sleep(0.1)
                self.EntrarNaSecaoCritica()
                self.LiberarSecaoCritica()