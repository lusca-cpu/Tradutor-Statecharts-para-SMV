from token import TipoToken as tt

from lexico import Lexico


class Sintatico:
    def __init__(self):
        self.lex = None
        self.tokenAtual = None
        self.erro = False

    def interprete(self, name_file):
        if not self.lex is None:
            print("ERRO: Já existe um arquivo sendo processado.")
        else:
            self.lex = Lexico(name_file)
            self.lex.openFile()
            self.tokenAtual = self.lex.getToken()

            self.STATECHART()

            self.lex.closeFile()

            return not self.erro

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
            self.error = True
            (const, msg) = token
            print(
                f'ERRO DE SINTAXE [linha {self.tokenAtual.line}]: era esperado "{msg}" mas veio "{self.tokenAtual.lexema}"'
            )
            quit()

    def STATECHART(self):
        self.consome(tt.STATECHART)
        self.IDENTIFIER()
        self.consome(tt.OPENBRACES)

        if self.atualIgual(tt.DECLARATIONS):
            self.DECLARATIONS_SECTION()

        if self.atualIgual(tt.EVENTS):
            self.EVENTS_SECTION()

        self.STATES_SECTION()

        if self.atualIgual(tt.TRANSITIONS):
            self.TRANSITIONS_SECTION()

        self.consome(tt.CLOSEBRACES)

    def DECLARATIONS_SECTION(self):
        self.consome(tt.DECLARATIONS_SECTION)
        self.consome(tt.OPENBRACES)

        while self.atualIgual(tt.VARIEABLE_DECLARATION):
            self.VARIABLE_DECLARATION()

        self.consome(tt.CLOSEBRACES)

    def VARIABLE_DECLARATION(self):
        if self.atualIgual(tt.BOOL):
            self.consome(tt.BOOL)
            self.IDENTIFIER()

            if self.atualIgual(tt.EQUAL):
                self.consome(tt.EQUAL)
                self.BOOLEAN()

            self.consome(tt.SEMICOLON)

        elif self.atualIgual(tt.INT):
            self.consome(tt.INT)
            self.IDENTIFIER()
            self.RANGE()

            if self.atualIgual(tt.EQUAL):
                self.consome(tt.EQUAL)
                self.INTEGER()

            self.consome(tt.SEMICOLON)

        elif self.atualIgual(tt.ENUM):
            self.consome(tt.ENUM)
            self.IDENTIFIER()
            self.consome(tt.OPENBRACES)
            self.IDENTIFIER_LIST()
            self.consome(tt.CLOSEBRACES)

            if self.atualIgual(tt.EQUAL):
                self.consome(tt.EQUAL)
                self.IDENTIFIER()

            self.consome(tt.SEMICOLON)

    def RANGE(self):
        self.consome(tt.OPENBRACKET)
        self.INTEGER()
        self.consome(tt.RANGE)
        self.INTEGER()
        self.consome(tt.CLOSEBRACKET)

    def EVENTS_SECTION(self):
        self.consome(tt.EVENTS)
        self.consome(tt.OPENBRACES)

        while self.atualIgual(tt.EVENT):
            self.EVENTS_DECLARATION()

        self.consome(tt.CLOSEBRACES)

    def EVENTS_DECLARATION(self):
        self.consome(tt.EVENT)
        self.IDENTIFIER()
        self.consome(tt.SEMICOLON)

    def STATES_SECTION(self):
        self.consome(tt.STATES)
        self.consome(tt.OPENBRACES)

        while (self.atualIgual(tt.INITIAL) or self.atualIgual(tt.FINAL) or self.atualIgual(tt.STATE) or self.atualIgual(tt.PARALLEL)):
            self.STATE_DECLARATION()

        self.consome(tt.CLOSEBRACES)

    def STATE_DECLARATION(self):
        if self.atualIgual(tt.INITIAL):
            self.consome(tt.INITIAL)
            self.consome(tt.STATE)
            self.IDENTIFIER()

            if self.atualIgual(tt.OPENBRACES):
                self.COMPOSITE_STATE()
            else:
                self.SIMPLE_STATE()

        elif self.atualIgual(tt.FINAL):
            self.consome(tt.FINAL)
            self.consome(tt.STATE)
            self.IDENTIFIER()

            if self.atualIgual(tt.OPENBRACES):
                self.COMPOSITE_STATE()
            else:
                self.SIMPLE_STATE()

        elif self.atualIgual(tt.STATE):
            self.consome(tt.STATE)
            self.IDENTIFIER()

            if self.atualIgual(tt.OPENBRACES):
                self.COMPOSITE_STATE()
            else:
                self.SIMPLE_STATE()
        
        elif self.atualIgual(tt.PARALLEL):
            self.PARALLEL_STATE()

    def SIMPLE_STATE(self):
        if self.atualIgual(tt.OPENBRACES):
            self.STATE_BODY()

        self.consome(tt.SEMICOLON)

    def STATE_BODY(self):
        self.consome(tt.OPENBRACES)

        while (self.atualIgual(tt.ENTRY) or self.atualIgual(tt.EXIT) or self.atualIgual(tt.INTERNAL)):
            if self.atualIgual(tt.ENTRY):
                self.ENTRY_SECTION()
            elif self.atualIgual(tt.EXIT):
                self.EXIT_SECTION()
            elif self.atualIgual(tt.INTERNAL):
                self.INTERNAL_SECTION()

        self.consome(tt.CLOSEBRACES)

    def ENTRY_SECTION(self):
        self.consome(tt.ENTRY)
        self.consome(tt.MULTIPLICATIVE)
        self.ACTION_LIST()
        self.consome(tt.SEMICOLON)

    def EXIT_SECTION(self):
        self.consome(tt.EXIT)
        self.consome(tt.MULTIPLICATIVE)
        self.ACTION_LIST()
        self.consome(tt.SEMICOLON)

    def INTERNAL_SECTION(self):
        self.consome(tt.INTERNAL)

        if self.atualIgual(tt.ON):
            self.consome(tt.ON)
            self.IDENTIFIER()

        if self.atualIgual(tt.WHEN):
            self.consome(tt.WHEN)
            self.EXPRESSION()

        if self.atualIgual(tt.MULTIPLICATIVE):
            self.consome(tt.MULTIPLICATIVE)
            self.ACTION_LIST()

        self.consome(tt.SEMICOLON)

    def COMPOSITE_STATE(self):
        self.consome(tt.OPENBRACES)

        if self.atualIgual(tt.DECLARATIONS):
            self.DECLARATIONS_SECTION()

        if self.atualIgual(tt.STATES):
            self.STATES_SECTION()

        if self.atualIgual(tt.TRANSITIONS):
            self.TRANSITIONS_SECTION()

        while (self.atualIgual(tt.ENTRY) or self.atualIgual(tt.EXIT)):
            if self.atualIgual(tt.ENTRY):
                self.ENTRY_SECTION()
            elif self.atualIgual(tt.EXIT):
                self.EXIT_SECTION()

        self.consome(tt.CLOSEBRACES)
        self.consome(tt.SEMICOLON)

    def PARALLEL_STATE(self): #ESTA INCOMPLETA, PRECISA SER IMPLEMENTADA
        self.consome(tt.PARALLEL)
        self.consome(tt.STATE)
        self.IDENTIFIER()

    def PARALLEL_REGION(self):
        self.consome(tt.REGION)
        self.IDENTIFIER()
        self.consome(tt.OPENBRACES)
        self.STATES_SECTION()

        if self.atualIgual(tt.TRANSITIONS):
            self.TRANSITIONS_SECTION()

        self.consome(tt.CLOSEBRACES)

    def TRANSITIONS_SECTION(self):
        self.consome(tt.TRANSITIONS)
        self.consome(tt.OPENBRACES)

        while self.atualIgual(tt. IDENTIFIER):
            self.TRANSITION()

        self.consome(tt.CLOSEBRACES)

    def TRANSITION(self):
        self.IDENTIFIER()
        self.consome(tt.ARROW)
        self.IDENTIFIER()

        if self.atualIgual(tt.ON): 
            self.consome(tt.ON)
            self.IDENTIFIER()

        if self.atualIgual(tt.WHEN):
            self.consome(tt.WHEN)
            self.EXPRESSION()

        if self.atualIgual(tt.MULTIPLICATIVE):
            self.consome(tt.MULTIPLICATIVE)
            self.ACTION_LIST()

        self.consome(tt.SEMICOLON)

    def ACTION_LIST(self):
        self.ASSIGNMENT()

        while self.atualIgual(tt.COMMA):
            self.consome(tt.COMMA)
            self.ASSIGNMENT()

    def ASSIGNMENT(self):
        self.IDENTIFIER()
        self.consome(tt.EQUAL)
        self.EXPRESSION()

    def EXPRESSION(self):
        self.LOGICAL_OR_EXPRESSION()

    def LOGICAL_OR_EXPRESSION(self):
        self.LOGICAL_AND_EXPRESSION()

        while self.atualIgual(tt.OR):
            self.consome(tt.OR)
            self.LOGICAL_AND_EXPRESSION()

    def LOGICAL_AND_EXPRESSION(self):
        self.EQUALITY_EXPRESSION()

        while self.atualIgual(tt.AND):
            self.consome(tt.AND)
            self.EQUALITY_EXPRESSION()

    def EQUALITY_EXPRESSION(self):
        self.RELATIONAL_EXPRESSION()

        while self.atualIgual(tt.EQUAL):
            self.consome(tt.EQUAL)
            self.RELATIONAL_EXPRESSION()

    def RELATIONAL_EXPRESSION(self):
        self.ADDITIVE_EXPRESSION()

        if self.atualIgual(tt.RELATIONAL):
            self.consome(tt.RELATIONAL)
            self.ADDITIVE_EXPRESSION()

    def ADDITIVE_EXPRESSION(self):
        self.MULTIPLICATIVE_EXPRESSION()

        while self.atualIgual(tt.ADDITIVE):
            self.consome(tt.ADDITIVE)
            self.MULTIPLICATIVE_EXPRESSION()

    def MULTIPLICATIVE_EXPRESSION(self):
        self.UNARY_EXPRESSION()

        while self.atualIgual(tt.MULTIPLICATIVE) or self.atualIgual(tt.MOD):
            if self.atualIgual(tt.MOD):
                self.consome(tt.MOD)
                self.UNARY_EXPRESSION()
            else:
                self.consome(tt.MULTIPLICATIVE)
                self.UNARY_EXPRESSION()

    def UNARY_EXPRESSION(self):
        if self.atualIgual(tt.NOT):
            self.consome(tt.NOT)
            self.UNARY_EXPRESSION()
        else:
            self.consome(tt.ADDITIVE)
            self.PRIMARY_EXPRESSION()

    def PRIMARY_EXPRESSION(self):
        if self.atualIgual(tt.IDENT):
            self.IDENTIFIER()
        elif self.atualIgual(tt.NUM):
            self.INTEGER()
        elif self.atualIgual(tt.TRUE):
            self.consome(tt.TRUE)
        elif self.atualIgual(tt.FALSE):
            self.consome(tt.FALSE)
        elif self.atualIgual(tt.OPENPAREN):
            self.consome(tt.OPENPAREN)
            self.EXPRESSION()
            self.consome(tt.CLOSEPAREN)

    def IDENTIFIER_LIST(self):
        self.IDENTIFIER()

        while self.atualIgual(tt.COMMA):
            self.consome(tt.COMMA)
            self.IDENTIFIER()

    def IDENTIFIER(self):
        self.consome(tt.IDENT)

        while (self.atualIgual(tt.IDENT) or self.atualIgual(tt.NUM) or self.atualIgual(tt.UNDERCORE)):
            if self.atualIgual(tt.IDENT):
                self.consome(tt.IDENT)
            elif self.atualIgual(tt.NUM):
                self.consome(tt.NUM)
            elif self.atualIgual(tt.UNDERCORE):
                self.consome(tt.UNDERCORE)

    def INTEGER(self):
        if self.atualIgual(tt.ADDITIVE):
            self.consome(tt.ADDITIVE)

        self.consome(tt.NUM)

        while self.atualIgual(tt.NUM):
            self.consome(tt.NUM)