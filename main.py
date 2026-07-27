from sintatico import Sintatico
from token import TipoToken

if __name__ == "__main__":
    nome_arquivo = "exem.txt"  
    
    sintatico = Sintatico()

    sintatico.interprete(nome_arquivo)

    if sintatico:
        print("Análise sintática concluída com sucesso!")

