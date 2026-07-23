from os import path
from token import TipoToken as tt, Token


class Lexico:
    reserved_word = {
        "statechart": tt.STATECHART, "state": tt.STATE, "states": tt.STATES, "initial": tt.INITIAL,"final": tt.FINAL, 
        "on": tt.ON, "declarations": tt.DECLARATIONS, "event": tt.EVENT, "events": tt.EVENTS, "entry": tt.ENTRY,
        "exit": tt.EXIT, "internal": tt.INTERNAL, "when": tt.WHEN, "parallel": tt.PARALLEL, "region": tt.REGION, 
        "transitions": tt.TRANSITIONS,"or": tt.OR, "and": tt.AND, "not": tt.NOT, "true": tt.TRUE, "false": tt.FALSE,
        "bool": tt.BOOL, "int": tt.INT, "enum": tt.ENUM, "string": tt.STRING, "mod": tt.MOD
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
                    return Token(tt.EOF, "eof", self.line)
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
                    return Token(tt.ERROR, "<" + char + ">", self.line)

            elif state == 2:
                # ESTADO PARA TRATAR NOME
                lexema += char
                char = self.getChar()

                if char is None or (not char.isalnum()):
                    self.ungetChar(char)
                    if lexema in Lexico.reserved_word:
                        return Token(Lexico.reserved_word[lexema], lexema, self.line)
                    else:
                        return Token(tt.IDENT, lexema, self.line)

            elif state == 3:
                # ESTADO PARA TRATAR NÚMEROS
                lexema += char
                char = self.getChar()

                if char is None or (not char.isdigit()):
                    self.ungetChar(char)
                    return Token(tt.NUM, lexema, self.line)

            elif state == 4:
                # ESTADO PARA TRATAR OS TOKENS PRIMITIVOS
                lexema += char

                if char == "{":
                    return Token(tt.OPENBRACES, lexema, self.line)
                
                elif char == "}":
                    return Token(tt.CLOSEBRACES, lexema, self.line)
                
                elif char == "(":
                    return Token(tt.OPENPAREN, lexema, self.line)
                
                elif char == ")":
                    return Token(tt.CLOSEPAREN, lexema, self.line)
                
                elif char == "[":
                    return Token(tt.OPENBRACKET, lexema, self.line)
                
                elif char == "]":
                    return Token(tt.CLOSEBRACKET, lexema, self.line)
                
                elif char == "/":
                    aux = self.getChar()
                    if (aux == "/") or (aux == "*"):
                        state = 5  # ESTADO PARA TRATAR COMENTÁRIOS
                    return Token(tt.MULTIPLICATIVE, lexema, self.line)
                
                elif char == "*":
                    return Token(tt.MULTIPLICATIVE, lexema, self.line)

                elif char == ",":
                    return Token(tt.COMMA, lexema, self.line)
                
                elif char == ";":
                    return Token(tt.SEMICOLON, lexema, self.line)
                
                elif char == "_":
                    return Token(tt.UNDERCORE, lexema, self.line)
                
                elif char == "-":
                    aux = self.getChar()
                    if aux == ">":
                        lexema = char + aux
                        return Token(tt.ARROW, lexema, self.line)
                    else:
                        self.ungetChar(aux)
                        return Token(tt.ADDITIVE, lexema, self.line)
                    
                elif char == "+":
                    return Token(tt.ADDITIVE, lexema, self.line)
                    
                elif char == "=":   
                    return Token(tt.EQUAL, lexema, self.line)
                
                elif char == "<" or char == ">":
                    aux = self.getChar()
                    if aux == "=":
                        lexema = char + aux
                        return Token(tt.RELATIONAL, lexema, self.line)
                    else:
                        self.ungetChar(aux)
                        return Token(tt.RELATIONAL, lexema, self.line)
                    
                elif char == ".":
                    aux = self.getChar()
                    if aux == ".":
                        lexema = char + aux
                        return Token(tt.RANGE, lexema, self.line)
                    else:
                        self.ungetChar(aux)
                        return Token(tt.ERROR, "<" + char + ">", self.line)

                elif char == "!":
                    aux = self.getChar()
                    if aux == "=":
                        lexema = char + aux
                        return Token(tt.EQUAL, lexema, self.line)
                    else:
                        self.ungetChar(aux)
                        return Token(tt.ERROR, "<" + char + ">", self.line)

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
