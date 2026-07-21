from os import path
from token import TipoToken, Token


class Lexico:
    reserved_word = {
        "statechart": TipoToken.STATECHART, "state": TipoToken.STATE, "states": TipoToken.STATES, "initial": TipoToken.INITIAL,"final": TipoToken.FINAL, 
        "on": TipoToken.ON, "declarations": TipoToken.DECLARATIONS, "event": TipoToken.EVENT, "events": TipoToken.EVENTS, "entry": TipoToken.ENTRY,
        "exit": TipoToken.EXIT, "internal": TipoToken.INTERNAL, "when": TipoToken.WHEN, "parallel": TipoToken.PARALLEL, "region": TipoToken.REGION, 
        "transitions": TipoToken.TRANSITIONS,"or": TipoToken.OR, "and": TipoToken.AND, "not": TipoToken.NOT, "true": TipoToken.TRUE, "false": TipoToken.FALSE,
        "bool": TipoToken.BOOL, "int": TipoToken.INT, "enum": TipoToken.ENUM, "string": TipoToken.STRING, "mod": TipoToken.MOD
    }

    def __init__(self, name_file):
        self.name_file = name_file
        self.file = None

    def openFile(self):
        if not self.file is None:
            print("Erro, arquivo ja aberto.")
            quit()
        elif path.exists(self.name_file):
            self.file = open(self.name_file, "r")
            self.buffer = ""
            self.line = 1
        else:
            print(f"Erro, arquivo {self.name_file} não existe.")
            quit()

    def closeFile(self):
        if self.file is None:
            print("Erro, não tem arquivo aberto.")
            quit()
        else:
            self.file.close()

    def getChar(self):
        # Retorna o próximo caractere do arquivo.
        # Caso exista conteúdo no buffer, retorna primeiro do buffer.
        # Caso contrário, lê do arquivo.

        if self.file is None:
            print("Erro, não tem arquivo aberto.")
            quit()
        elif len(self.buffer) > 0:
            c = self.buffer[0]
            self.buffer = self.buffer[1:]
            return c
        else:
            c = self.file.read(1)

            if len(c) == 0:
                return None
            else:
                return c.lower()

    def ungetChar(self, c):
        # Devolve um caractere para o buffer,
        # permitindo que ele seja lido novamente depois.

        if not (c is None):
            self.buffer = self.buffer + c

    def getToken(self):
        lexema = ""
        state = 1
        char = None

        while True:
            if state == 1:
                char = self.getChar()

                if char is None:
                    return Token(TipoToken.EOF, "eof", self.line)
                elif char in {" ", "\t", "\n"}:
                    if char == "\n":
                        self.line += 1
                elif char.isalpha():
                    state = 2  # ESTADO PARA TRATAR NOME
                elif char.isdigit():
                    state = 3  # ESTADO PARA TRATAR NÚMEROS
                elif char in {"{", "}", "(", ")", "[", "]", "/", "*", ",", ";", "_", "-", "+", "=", "<", ">", ".", "!"}:
                    state = 4  # ESTADO PARA TRATAR OS TOKENS PRIMITIVOS
                else:
                    return Token(TipoToken.ERROR, "<" + char + ">", self.line)

            elif state == 2:
                # ESTADO PARA TRATAR NOME
                lexema += char
                char = self.getChar()

                if char is None or (not char.isalnum()):
                    self.ungetChar(char)
                    if lexema in Lexico.reserved_word:
                        return Token(Lexico.reserved_word[lexema], lexema, self.line)
                    else:
                        return Token(TipoToken.IDENT, lexema, self.line)

            elif state == 3:
                # ESTADO PARA TRATAR NÚMEROS
                lexema += char
                char = self.getChar()

                if char is None or (not char.isdigit()):
                    self.ungetChar(char)
                    return Token(TipoToken.NUM, lexema, self.line)

            elif state == 4:
                # ESTADO PARA TRATAR OS TOKENS PRIMITIVOS
                lexema += char

                if char == "{":
                    return Token(TipoToken.OPENBRACES, lexema, self.line)
                
                elif char == "}":
                    return Token(TipoToken.CLOSEBRACES, lexema, self.line)
                
                elif char == "(":
                    return Token(TipoToken.OPENPAREN, lexema, self.line)
                
                elif char == ")":
                    return Token(TipoToken.CLOSEPAREN, lexema, self.line)
                
                elif char == "[":
                    return Token(TipoToken.OPENBRACKET, lexema, self.line)
                
                elif char == "]":
                    return Token(TipoToken.CLOSEBRACKET, lexema, self.line)
                
                elif char == "/":
                    aux = self.getChar()
                    if (aux == "/") or (aux == "*"):
                        state = 5  # ESTADO PARA TRATAR COMENTÁRIOS
                    return Token(TipoToken.MULTIPLICATIVE, lexema, self.line)
                
                elif char == "*":
                    return Token(TipoToken.MULTIPLICATIVE, lexema, self.line)

                elif char == ",":
                    return Token(TipoToken.COMMA, lexema, self.line)
                
                elif char == ";":
                    return Token(TipoToken.SEMICOLON, lexema, self.line)
                
                elif char == "_":
                    return Token(TipoToken.UNDERCORE, lexema, self.line)
                
                elif char == "-":
                    aux = self.getChar()
                    if aux == ">":
                        lexema = char + aux
                        return Token(TipoToken.ARROW, lexema, self.line)
                    else:
                        self.ungetChar(aux)
                        return Token(TipoToken.ADDITIVE, lexema, self.line)
                    
                elif char == "+":
                    return Token(TipoToken.ADDITIVE, lexema, self.line)
                    
                elif char == "=":   
                    return Token(TipoToken.EQUAL, lexema, self.line)
                
                elif char == "<" or char == ">":
                    aux = self.getChar()
                    if aux == "=":
                        lexema = char + aux
                        return Token(TipoToken.RELATIONAL, lexema, self.line)
                    else:
                        self.ungetChar(aux)
                        return Token(TipoToken.RELATIONAL, lexema, self.line)
                    
                elif char == ".":
                    aux = self.getChar()
                    if aux == ".":
                        lexema = char + aux
                        return Token(TipoToken.RANGE, lexema, self.line)
                    else:
                        self.ungetChar(aux)
                        return Token(TipoToken.ERROR, "<" + char + ">", self.line)

                elif char == "!":
                    aux = self.getChar()
                    if aux == "=":
                        lexema = char + aux
                        return Token(TipoToken.EQUAL, lexema, self.line)
                    else:
                        self.ungetChar(aux)
                        return Token(TipoToken.ERROR, "<" + char + ">", self.line)

            elif state == 5:
                # CONSUMINDO COMENTARIO
                if aux == '/':
                    while (not char is None) and (char != '\n'):
                        char = self.getChar()                    
                else: 
                    while (not char is None):
                        char = self.getChar()
                        if char == '*':
                            aux = self.getChar()
                            if aux == '/':
                                break
                        elif char == None:
                            print(f'ERRO LÉXICO NA LINHA {self.linha}!')
                            quit()
                self.ungetChar(char)
                lexema = '' 
                state = 1
