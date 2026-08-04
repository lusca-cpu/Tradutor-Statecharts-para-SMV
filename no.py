class No:
    """Classe base de todos os nós da AST (Árvore Sintática Abstrata)."""
    pass


# ==================== STATECHART ====================

class StatechartNode(No):
    def __init__(self, nome, declaracoes=None, eventos=None, estados=None, transicoes=None):
        self.nome = nome
        self.declaracoes = declaracoes if declaracoes is not None else []
        self.eventos = eventos if eventos is not None else []
        self.estados = estados if estados is not None else []
        self.transicoes = transicoes if transicoes is not None else []

    def __repr__(self):
        return f"StatechartNode(nome={self.nome!r}, declaracoes={self.declaracoes}, eventos={self.eventos}, estados={self.estados}, transicoes={self.transicoes})"


# ==================== DECLARATIONS ====================

class DeclaracaoVariavelNode(No):
    def __init__(self, tipo, nome, range_min=None, range_max=None, valores_enum=None, valor_inicial=None):
        self.tipo = tipo
        self.nome = nome
        self.range_min = range_min
        self.range_max = range_max
        self.valores_enum = valores_enum if valores_enum is not None else []
        self.valor_inicial = valor_inicial

    def __repr__(self):
        return f"DeclaracaoVariavelNode(tipo={self.tipo!r}, nome={self.nome!r}, range=({self.range_min},{self.range_max}), enum={self.valores_enum}, valor_inicial={self.valor_inicial})"


# ==================== EVENTS ====================

class EventoNode(No):
    def __init__(self, nome):
        self.nome = nome

    def __repr__(self):
        return f"EventoNode(nome={self.nome!r})"


# ==================== STATES ====================

class EstadoNode(No):
    def __init__(self, nome, inicial=False, final=False,
                 entry=None, exit=None, internos=None,
                 declaracoes=None, estados_filhos=None, transicoes=None):
        self.nome = nome
        self.inicial = inicial
        self.final = final
        self.entry = entry if entry is not None else []
        self.exit = exit if exit is not None else []
        self.internos = internos if internos is not None else []
        self.declaracoes = declaracoes if declaracoes is not None else []
        self.estados_filhos = estados_filhos if estados_filhos is not None else []
        self.transicoes = transicoes if transicoes is not None else []

    def __repr__(self):
        return (f"EstadoNode(nome={self.nome!r}, inicial={self.inicial}, final={self.final}, "
                f"entry={self.entry}, exit={self.exit}, internos={self.internos}, "
                f"declaracoes={self.declaracoes}, estados_filhos={self.estados_filhos}, transicoes={self.transicoes})")


class TransicaoInternaNode(No):
    def __init__(self, evento=None, condicao=None, acoes=None):
        self.evento = evento
        self.condicao = condicao
        self.acoes = acoes if acoes is not None else []

    def __repr__(self):
        return f"TransicaoInternaNode(evento={self.evento!r}, condicao={self.condicao}, acoes={self.acoes})"


class EstadoParaleloNode(No):
    def __init__(self, nome, regioes=None):
        self.nome = nome
        self.regioes = regioes if regioes is not None else []

    def __repr__(self):
        return f"EstadoParaleloNode(nome={self.nome!r}, regioes={self.regioes})"


class RegiaoNode(No):
    def __init__(self, nome, estados=None, transicoes=None):
        self.nome = nome
        self.estados = estados if estados is not None else []
        self.transicoes = transicoes if transicoes is not None else []

    def __repr__(self):
        return f"RegiaoNode(nome={self.nome!r}, estados={self.estados}, transicoes={self.transicoes})"


# ==================== TRANSITIONS ====================

class TransicaoNode(No):
    def __init__(self, origem, destino, evento=None, condicao=None, acoes=None):
        self.origem = origem
        self.destino = destino
        self.evento = evento
        self.condicao = condicao
        self.acoes = acoes if acoes is not None else []

    def __repr__(self):
        return f"TransicaoNode(origem={self.origem!r}, destino={self.destino!r}, evento={self.evento!r}, condicao={self.condicao}, acoes={self.acoes})"


class AtribuicaoNode(No):
    def __init__(self, identificador, expressao):
        self.identificador = identificador
        self.expressao = expressao

    def __repr__(self):
        return f"AtribuicaoNode(identificador={self.identificador!r}, expressao={self.expressao})"


# ==================== EXPRESSIONS ====================

class ExpressaoBinariaNode(No):
    def __init__(self, operador, esquerda, direita):
        self.operador = operador
        self.esquerda = esquerda
        self.direita = direita

    def __repr__(self):
        return f"({self.esquerda} {self.operador} {self.direita})"


class ExpressaoUnariaNode(No):
    def __init__(self, operador, operando):
        self.operador = operador
        self.operando = operando

    def __repr__(self):
        return f"({self.operador}{self.operando})"


class IdentificadorNode(No):
    def __init__(self, nome):
        self.nome = nome

    def __repr__(self):
        return f"{self.nome}"


class NumeroNode(No):
    def __init__(self, valor):
        self.valor = valor

    def __repr__(self):
        return f"{self.valor}"


class BooleanoNode(No):
    def __init__(self, valor):
        self.valor = valor

    def __repr__(self):
        return f"{self.valor}"