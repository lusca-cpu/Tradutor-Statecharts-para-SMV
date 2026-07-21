from lexico import Lexico
from token import TipoToken

def main():
    nome_arquivo = "exem.txt"  # ajuste o caminho se necessário

    lexico = Lexico(nome_arquivo)
    lexico.openFile()

    while True:
        token = lexico.getToken()

        print(f"Linha {token.line:>3} | {token.msg:<15} | lexema: '{token.lexema}'")

        if token.tipo == TipoToken.EOF:
            break

        if token.tipo == TipoToken.ERROR:
            print(f"Erro léxico encontrado na linha {token.line}: {token.lexema}")
            break

    lexico.closeFile()


if __name__ == "__main__":
    main()