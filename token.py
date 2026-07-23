class TipoToken:
    # PALAVRAS RESERVADAS
    STATECHART = (1, "statechart")
    STATE = (2, "state")
    STATES = (3, "states")
    INITIAL = (4, "initial")
    FINAL = (5, "final")
    ON = (6, "on")
    DECLARATIONS = (7, "declarations") 
    EVENT = (8, "event")
    EVENTS = (9, "events")
    ENTRY = (10, "entry")
    EXIT = (11, "exit")
    INTERNAL = (12, "internal")
    WHEN = (13, "when")
    PARALLEL = (14, "parallel")
    REGION = (15, "region")
    TRANSITIONS = (16, "transitions")
    OR = (17, "or")
    AND = (18, "and")
    NOT = (19, "not")
    TRUE = (20, "true")
    FALSE = (21, "false")
    MOD = (22, "mod")

    # TIPOS BASICOS DA LINGUAGEM STATECHART
    BOOL = (23, "bool")
    INT = (24, "int")
    ENUM = (25, "enum")
    STRING = (26, "string")

    # TOKEN PRIMITIVO
    OPENBRACES = (27, "{")
    CLOSEBRACES = (28, "}")
    OPENPAREN = (29, "(")
    CLOSEPAREN = (30, ")")
    OPENBRACKET = (31, "[")
    CLOSEBRACKET = (32, "]")
    COMMA = (33, ",")
    SEMICOLON = (34, ";")
    UNDERCORE = (35, "_")
    ARROW = (36, "->")
    RANGE = (37, "..")
    EQUAL = (38, "=, !=")
    RELATIONAL = (39, "<, >, <=, >=")
    ADDITIVE = (40, "+, -")
    MULTIPLICATIVE = (41, "*, /")

    # TOKEN PARA O NOME DE VARIAVEIS, FUNCOES E OUTROS IDENTIFICADORES
    IDENT = (42, "ident")

    # TOKEN DE NUMERO
    NUM = (43, "num")

    # TOKEN DE ERRO
    ERROR = (44, "erro")

    # TOKEN FIM DO ARQUIVO
    EOF = (45, "eof")


class Token:
    def __init__(self, tipo, lexema, line):
        self.tipo = tipo
        (const, msg) = tipo
        self.const = const
        self.msg = msg
        self.lexema = lexema
        self.line = line
