from sintatico import Sintatico
from token import TipoToken

def main():
    nome_arquivo = "exem.txt"  # ajuste o caminho se necessário

    sintatico = Sintatico(nome_arquivo)

    while True:
        token = sintatico.getToken()

        if token.tipo == TipoToken.EOF:
            break

if __name__ == "__main__":
    main()