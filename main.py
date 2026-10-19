import os
import sys

from sintatico import Sintatico
from tradutor import TradutorNuSMV, TraducaoErro

PASTA_EXEMPLOS = "exemple"
PASTA_SAIDA = "saida"


def caminho_saida_unico(nome):
    """Devolve saida/nome.smv; se já existir, saida/nome_1.smv, nome_2.smv..."""
    caminho = os.path.join(PASTA_SAIDA, f"{nome}.smv")
    contador = 1
    while os.path.exists(caminho):
        caminho = os.path.join(PASTA_SAIDA, f"{nome}_{contador}.smv")
        contador += 1
    return caminho


if __name__ == "__main__":
    nome = input("Digite o nome do exemplo: ") if len(sys.argv) <= 1 else sys.argv[1]
    nome = os.path.splitext(nome.strip())[0]  # aceita "teste" ou "teste.txt"

    entrada = os.path.join(PASTA_EXEMPLOS, nome + ".txt")
    if not os.path.isfile(entrada):
        print(f"ERRO: arquivo '{entrada}' não encontrado.")
        sys.exit(1)

    arvore = Sintatico().interprete(entrada)
    if arvore is None:
        sys.exit(1)
    print("Análise sintática concluída com sucesso!")

    try:
        codigo = TradutorNuSMV().traduzir(arvore)
    except TraducaoErro as erro:
        print(f"ERRO SEMÂNTICO: {erro}")
        sys.exit(1)

    os.makedirs(PASTA_SAIDA, exist_ok=True)
    saida = caminho_saida_unico(nome)

    with open(saida, "w", encoding="utf-8") as f:
        f.write(codigo)
    print(f"Tradução gravada em {saida}")