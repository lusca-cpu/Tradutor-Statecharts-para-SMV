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
