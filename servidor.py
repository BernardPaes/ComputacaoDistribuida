import socket
import threading

class Servidor:
    def __init__(self, MeuId, Configuracao, Cliente):
        self.MeuId = MeuId
        self.Configuracao = Configuracao
        self.Cliente = Cliente

    def IniciarServidor(self):
        host, porta = self.Configuracao[str(self.MeuId)]
        servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        servidor.bind((host, porta))
        servidor.listen()
        print(f"[Servidor {self.MeuId}] Aguardando conexões em {host}:{porta}")

        while True:
            conexao, endereco = servidor.accept()
            threading.Thread(target=self.ProcessarConexao, args=(conexao,)).start()

    def ProcessarConexao(self, conexao):
        try:
            dados = conexao.recv(1024).decode()
            if 'timestamp' in dados or dados.startswith('{'):
                if 'ok' in dados:
                    self.Cliente.ReceberOk()
                else:
                    self.Cliente.ReceberRequisicao(dados)
        except Exception as e:
            print(f"[Servidor {self.MeuId}] Erro ao processar conexão: {e}")
        finally:
            conexao.close()