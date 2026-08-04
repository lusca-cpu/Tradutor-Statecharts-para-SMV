from token import TipoToken as tt

from lexico import Lexico
from no import (
    StatechartNode,
    DeclaracaoVariavelNode,
    EventoNode,
    EstadoNode,
    TransicaoInternaNode,
    EstadoParaleloNode,
    RegiaoNode,
    TransicaoNode,
    AtribuicaoNode,
    ExpressaoBinariaNode,
    ExpressaoUnariaNode,
    IdentificadorNode,
    NumeroNode,
    BooleanoNode,
)


class Sintatico:
    def __init__(self):
        self.lex = None
        self.tokenAtual = None
        self.erro = False

    def interprete(self, name_file):
        if not self.lex is None:
            print("ERRO: Já existe um arquivo sendo processado.")
            return None
        else:
            self.lex = Lexico(name_file)
            self.lex.openFile()
            self.tokenAtual = self.lex.getToken()

            arvore = self.STATECHART()

            self.lex.closeFile()

            return arvore if not self.erro else None

    def atualIgual(self, token):
        (const, msg) = token
        return self.tokenAtual.const == const

    def consome(self, token):
        if self.atualIgual(token):
            (const, msg) = token
            ultimoToken = self.tokenAtual.lexema
            self.tokenAtual = self.lex.getToken()
            return ultimoToken

        else:
            self.erro = True
            (const, msg) = token
            print(
                f'ERRO DE SINTAXE [linha {self.tokenAtual.line}]: era esperado "{msg}" mas veio "{self.tokenAtual.lexema}"'
            )
            quit()

    # ==================== STATECHART ====================

    def STATECHART(self):
        self.consome(tt.STATECHART)
        nome = self.IDENTIFIER()
        self.consome(tt.OPENBRACES)

        declaracoes = []
        if self.atualIgual(tt.DECLARATIONS):
            declaracoes = self.DECLARATIONS_SECTION()

        eventos = []
        if self.atualIgual(tt.EVENTS):
            eventos = self.EVENTS_SECTION()

        estados = self.STATES_SECTION()

        transicoes = []
        if self.atualIgual(tt.TRANSITIONS):
            transicoes = self.TRANSITIONS_SECTION()

        self.consome(tt.CLOSEBRACES)

        return StatechartNode(nome, declaracoes, eventos, estados, transicoes)

    # ==================== DECLARATIONS ====================

    def DECLARATIONS_SECTION(self):
        self.consome(tt.DECLARATIONS)
        self.consome(tt.OPENBRACES)

        declaracoes = []
        while (self.atualIgual(tt.BOOL) or self.atualIgual(tt.INT) or self.atualIgual(tt.ENUM)):
            declaracoes.append(self.VARIABLE_DECLARATION())

        self.consome(tt.CLOSEBRACES)
        return declaracoes

    def VARIABLE_DECLARATION(self):
        if self.atualIgual(tt.BOOL):
            self.consome(tt.BOOL)
            nome = self.IDENTIFIER()

            valor = None
            if self.atualIgual(tt.EQUAL):
                self.consome(tt.EQUAL)
                valor = self.BOOLEAN()

            self.consome(tt.SEMICOLON)
            return DeclaracaoVariavelNode("bool", nome, valor_inicial=valor)

        elif self.atualIgual(tt.INT):
            self.consome(tt.INT)
            nome = self.IDENTIFIER()
            rmin, rmax = self.RANGE()

            valor = None
            if self.atualIgual(tt.EQUAL):
                self.consome(tt.EQUAL)
                valor = self.INTEGER()

            self.consome(tt.SEMICOLON)
            return DeclaracaoVariavelNode("int", nome, range_min=rmin, range_max=rmax, valor_inicial=valor)

        elif self.atualIgual(tt.ENUM):
            self.consome(tt.ENUM)
            nome = self.IDENTIFIER()
            self.consome(tt.OPENBRACES)
            valores = self.IDENTIFIER_LIST()
            self.consome(tt.CLOSEBRACES)

            valor = None
            if self.atualIgual(tt.EQUAL):
                self.consome(tt.EQUAL)
                valor = self.IDENTIFIER()

            self.consome(tt.SEMICOLON)
            return DeclaracaoVariavelNode("enum", nome, valores_enum=valores, valor_inicial=valor)

    def RANGE(self):
        self.consome(tt.OPENBRACKET)
        minimo = self.INTEGER()
        self.consome(tt.RANGE)
        maximo = self.INTEGER()
        self.consome(tt.CLOSEBRACKET)
        return (minimo, maximo)

    # ==================== EVENTS ====================

    def EVENTS_SECTION(self):
        self.consome(tt.EVENTS)
        self.consome(tt.OPENBRACES)

        eventos = []
        while self.atualIgual(tt.EVENT):
            eventos.append(self.EVENTS_DECLARATION())

        self.consome(tt.CLOSEBRACES)
        return eventos

    def EVENTS_DECLARATION(self):
        self.consome(tt.EVENT)
        nome = self.IDENTIFIER()
        self.consome(tt.SEMICOLON)
        return EventoNode(nome)

    # ==================== STATES ====================

    def STATES_SECTION(self):
        self.consome(tt.STATES)
        self.consome(tt.OPENBRACES)

        estados = []
        while (self.atualIgual(tt.INITIAL) or self.atualIgual(tt.FINAL)
               or self.atualIgual(tt.STATE) or self.atualIgual(tt.PARALLEL)):
            estados.append(self.STATE_DECLARATION())

        self.consome(tt.CLOSEBRACES)
        return estados

    def STATE_DECLARATION(self):
        inicial = False
        final = False

        if self.atualIgual(tt.INITIAL):
            self.consome(tt.INITIAL)
            inicial = True
        elif self.atualIgual(tt.FINAL):
            self.consome(tt.FINAL)
            final = True

        if self.atualIgual(tt.PARALLEL):
            return self.PARALLEL_STATE()

        self.consome(tt.STATE)
        nome = self.IDENTIFIER()

        estado = EstadoNode(nome, inicial=inicial, final=final)

        if self.atualIgual(tt.OPENBRACES):
            self.consome(tt.OPENBRACES)

            if (self.atualIgual(tt.ENTRY) or self.atualIgual(tt.EXIT) or self.atualIgual(tt.INTERNAL)):
                # simple_state com state_body
                self.STATE_BODY_CONTEUDO(estado)
            else:
                # composite_state
                self.COMPOSITE_STATE_CONTEUDO(estado)

            self.consome(tt.CLOSEBRACES)
            self.consome(tt.SEMICOLON)
        else:
            # simple_state sem corpo
            self.consome(tt.SEMICOLON)

        return estado

    def STATE_BODY_CONTEUDO(self, estado):
        # "{" já foi consumido por quem chamou
        while (self.atualIgual(tt.ENTRY) or self.atualIgual(tt.EXIT) or self.atualIgual(tt.INTERNAL)):
            if self.atualIgual(tt.ENTRY):
                estado.entry = self.ENTRY_SECTION()
            elif self.atualIgual(tt.EXIT):
                estado.exit = self.EXIT_SECTION()
            elif self.atualIgual(tt.INTERNAL):
                estado.internos.append(self.INTERNAL_SECTION())

    def ENTRY_SECTION(self):
        self.consome(tt.ENTRY)
        self.consome(tt.MULTIPLICATIVE)
        acoes = self.ACTION_LIST()
        self.consome(tt.SEMICOLON)
        return acoes

    def EXIT_SECTION(self):
        self.consome(tt.EXIT)
        self.consome(tt.MULTIPLICATIVE)
        acoes = self.ACTION_LIST()
        self.consome(tt.SEMICOLON)
        return acoes

    def INTERNAL_SECTION(self):
        self.consome(tt.INTERNAL)

        evento = None
        if self.atualIgual(tt.ON):
            self.consome(tt.ON)
            evento = self.IDENTIFIER()

        condicao = None
        if self.atualIgual(tt.WHEN):
            self.consome(tt.WHEN)
            condicao = self.EXPRESSION()

        acoes = []
        if self.atualIgual(tt.MULTIPLICATIVE):
            self.consome(tt.MULTIPLICATIVE)
            acoes = self.ACTION_LIST()

        self.consome(tt.SEMICOLON)
        return TransicaoInternaNode(evento, condicao, acoes)

    def COMPOSITE_STATE_CONTEUDO(self, estado):
        # "{" já foi consumido por quem chamou
        if self.atualIgual(tt.DECLARATIONS):
            estado.declaracoes = self.DECLARATIONS_SECTION()

        if self.atualIgual(tt.STATES):
            estado.estados_filhos = self.STATES_SECTION()

        if self.atualIgual(tt.TRANSITIONS):
            estado.transicoes = self.TRANSITIONS_SECTION()

        while (self.atualIgual(tt.ENTRY) or self.atualIgual(tt.EXIT)):
            if self.atualIgual(tt.ENTRY):
                estado.entry = self.ENTRY_SECTION()
            elif self.atualIgual(tt.EXIT):
                estado.exit = self.EXIT_SECTION()

    def PARALLEL_STATE(self):
        self.consome(tt.PARALLEL)
        self.consome(tt.STATE)
        nome = self.IDENTIFIER()
        self.consome(tt.OPENBRACES)

        regioes = [self.PARALLEL_REGION(), self.PARALLEL_REGION()]

        while self.atualIgual(tt.REGION):
            regioes.append(self.PARALLEL_REGION())

        self.consome(tt.CLOSEBRACES)
        self.consome(tt.SEMICOLON)

        return EstadoParaleloNode(nome, regioes)

    def PARALLEL_REGION(self):
        self.consome(tt.REGION)
        nome = self.IDENTIFIER()
        self.consome(tt.OPENBRACES)
        estados = self.STATES_SECTION()

        transicoes = []
        if self.atualIgual(tt.TRANSITIONS):
            transicoes = self.TRANSITIONS_SECTION()

        self.consome(tt.CLOSEBRACES)
        return RegiaoNode(nome, estados, transicoes)

    # ==================== TRANSITIONS ====================

    def TRANSITIONS_SECTION(self):
        self.consome(tt.TRANSITIONS)
        self.consome(tt.OPENBRACES)

        transicoes = []
        while self.atualIgual(tt.IDENT):
            transicoes.append(self.TRANSITION())

        self.consome(tt.CLOSEBRACES)
        return transicoes

    def TRANSITION(self):
        origem = self.IDENTIFIER()
        self.consome(tt.ARROW)
        destino = self.IDENTIFIER()

        evento = None
        if self.atualIgual(tt.ON):
            self.consome(tt.ON)
            evento = self.IDENTIFIER()

        condicao = None
        if self.atualIgual(tt.WHEN):
            self.consome(tt.WHEN)
            condicao = self.EXPRESSION()

        acoes = []
        if self.atualIgual(tt.MULTIPLICATIVE):
            self.consome(tt.MULTIPLICATIVE)
            acoes = self.ACTION_LIST()

        self.consome(tt.SEMICOLON)
        return TransicaoNode(origem, destino, evento, condicao, acoes)

    def ACTION_LIST(self):
        acoes = [self.ASSIGNMENT()]

        while self.atualIgual(tt.COMMA):
            self.consome(tt.COMMA)
            acoes.append(self.ASSIGNMENT())

        return acoes

    def ASSIGNMENT(self):
        identificador = self.IDENTIFIER()
        self.consome(tt.EQUAL)
        expressao = self.EXPRESSION()
        return AtribuicaoNode(identificador, expressao)

    # ==================== EXPRESSIONS ====================

    def EXPRESSION(self):
        return self.LOGICAL_OR_EXPRESSION()

    def LOGICAL_OR_EXPRESSION(self):
        esquerda = self.LOGICAL_AND_EXPRESSION()

        while self.atualIgual(tt.OR):
            op = self.consome(tt.OR)
            direita = self.LOGICAL_AND_EXPRESSION()
            esquerda = ExpressaoBinariaNode(op, esquerda, direita)

        return esquerda

    def LOGICAL_AND_EXPRESSION(self):
        esquerda = self.EQUALITY_EXPRESSION()

        while self.atualIgual(tt.AND):
            op = self.consome(tt.AND)
            direita = self.EQUALITY_EXPRESSION()
            esquerda = ExpressaoBinariaNode(op, esquerda, direita)

        return esquerda

    def EQUALITY_EXPRESSION(self):
        esquerda = self.RELATIONAL_EXPRESSION()

        while self.atualIgual(tt.EQUAL):
            op = self.consome(tt.EQUAL)
            direita = self.RELATIONAL_EXPRESSION()
            esquerda = ExpressaoBinariaNode(op, esquerda, direita)

        return esquerda

    def RELATIONAL_EXPRESSION(self):
        esquerda = self.ADDITIVE_EXPRESSION()

        if self.atualIgual(tt.RELATIONAL):
            op = self.consome(tt.RELATIONAL)
            direita = self.ADDITIVE_EXPRESSION()
            esquerda = ExpressaoBinariaNode(op, esquerda, direita)

        return esquerda

    def ADDITIVE_EXPRESSION(self):
        esquerda = self.MULTIPLICATIVE_EXPRESSION()

        while self.atualIgual(tt.ADDITIVE):
            op = self.consome(tt.ADDITIVE)
            direita = self.MULTIPLICATIVE_EXPRESSION()
            esquerda = ExpressaoBinariaNode(op, esquerda, direita)

        return esquerda

    def MULTIPLICATIVE_EXPRESSION(self):
        esquerda = self.UNARY_EXPRESSION()

        while self.atualIgual(tt.MULTIPLICATIVE) or self.atualIgual(tt.MOD):
            if self.atualIgual(tt.MOD):
                op = self.consome(tt.MOD)
            else:
                op = self.consome(tt.MULTIPLICATIVE)
            direita = self.UNARY_EXPRESSION()
            esquerda = ExpressaoBinariaNode(op, esquerda, direita)

        return esquerda

    def UNARY_EXPRESSION(self):
        if self.atualIgual(tt.NOT):
            op = self.consome(tt.NOT)
            operando = self.UNARY_EXPRESSION()
            return ExpressaoUnariaNode(op, operando)

        elif self.atualIgual(tt.ADDITIVE):
            op = self.consome(tt.ADDITIVE)
            operando = self.PRIMARY_EXPRESSION()
            return ExpressaoUnariaNode(op, operando)

        else:
            return self.PRIMARY_EXPRESSION()

    def PRIMARY_EXPRESSION(self):
        if self.atualIgual(tt.IDENT):
            return IdentificadorNode(self.IDENTIFIER())

        elif self.atualIgual(tt.NUM):
            return NumeroNode(self.INTEGER())

        elif self.atualIgual(tt.TRUE):
            self.consome(tt.TRUE)
            return BooleanoNode(True)

        elif self.atualIgual(tt.FALSE):
            self.consome(tt.FALSE)
            return BooleanoNode(False)

        elif self.atualIgual(tt.OPENPAREN):
            self.consome(tt.OPENPAREN)
            expressao = self.EXPRESSION()
            self.consome(tt.CLOSEPAREN)
            return expressao

        else:
            self.erro = True
            print(f'ERRO DE SINTAXE [linha {self.tokenAtual.line}]: expressão inválida, veio "{self.tokenAtual.lexema}"')
            quit()

    def BOOLEAN(self):
        if self.atualIgual(tt.TRUE):
            self.consome(tt.TRUE)
            return BooleanoNode(True)
        elif self.atualIgual(tt.FALSE):
            self.consome(tt.FALSE)
            return BooleanoNode(False)
        else:
            self.erro = True
            print(f'ERRO DE SINTAXE [linha {self.tokenAtual.line}]: era esperado "true" ou "false"')
            quit()

    # ==================== AUXILIARES ====================

    def IDENTIFIER_LIST(self):
        identificadores = [self.IDENTIFIER()]

        while self.atualIgual(tt.COMMA):
            self.consome(tt.COMMA)
            identificadores.append(self.IDENTIFIER())

        return identificadores

    def IDENTIFIER(self):
        nome = self.consome(tt.IDENT)

        while (self.atualIgual(tt.IDENT) or self.atualIgual(tt.NUM) or self.atualIgual(tt.UNDERCORE)):
            if self.atualIgual(tt.IDENT):
                nome += self.consome(tt.IDENT)
            elif self.atualIgual(tt.NUM):
                nome += self.consome(tt.NUM)
            elif self.atualIgual(tt.UNDERCORE):
                nome += self.consome(tt.UNDERCORE)

        return nome

    def INTEGER(self):
        sinal = ""
        if self.atualIgual(tt.ADDITIVE):
            sinal = self.consome(tt.ADDITIVE)

        numero = self.consome(tt.NUM)

        while self.atualIgual(tt.NUM):
            numero += self.consome(tt.NUM)

        return int(sinal + numero)