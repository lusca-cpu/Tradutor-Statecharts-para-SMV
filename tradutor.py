from collections import defaultdict

from no import EstadoNode, EstadoParaleloNode


class TraducaoErro(Exception):
    """Erro semântico encontrado durante a tradução."""
    pass


class Nivel:
    """Um nível da hierarquia. Cada nível vira UMA variável de estado no NuSMV:
    o topo (main_state), cada estado composto (<nome>_state) e cada região
    de um estado paralelo (<regiao>_state)."""

    def __init__(self, var, estados, transicoes, guarda_pai, ativo_inicial):
        self.var = var
        self.estados = estados
        self.transicoes = transicoes
        self.guarda_pai = guarda_pai          # ex.: "main_state = operando" (None no topo)
        self.ativo_inicial = ativo_inicial    # o pai está ativo no instante inicial?

        self.por_nome = {}
        for e in estados:
            if e.nome in self.por_nome:
                raise TraducaoErro(f"estado '{e.nome}' declarado duas vezes em '{var}'")
            self.por_nome[e.nome] = e


class TradutorNuSMV:
    """Visitor que traduz a AST de um statechart para um módulo NuSMV."""

    OPERADORES = {"and": "&", "or": "|", "not": "!"}

    def __init__(self):
        self.eventos = ["none"]
        self.vars_estado = {}                   # var -> (valores, valor inicial)
        self.vars_dados = {}                    # nome -> (domínio, valor inicial | None)
        self.casos_estado = defaultdict(list)   # var -> [(partes_da_condicao, valor)]
        self.casos_dados = defaultdict(list)    # var -> [(partes_da_condicao, expr)]

        self.pilha = []             # níveis em processamento (o último é o atual)
        self.estado_atual = None    # estado cujas transições internas estão sendo lidas
        self.ctx_regiao = None      # (guarda_pai, ativo) repassado às regiões

    # ------------------------------------------------------------------
    # Ponto de entrada
    # ------------------------------------------------------------------
    def traduzir(self, arvore):
        arvore.aceitar(self)
        return self.montar_saida()

    # ------------------------------------------------------------------
    # Raiz, declarações e eventos
    # ------------------------------------------------------------------
    def visitar_StatechartNode(self, n):
        for d in n.declaracoes:
            d.aceitar(self)
        for e in n.eventos:
            e.aceitar(self)
        self.tratar_nivel("main_state", n.estados, n.transicoes,
                          guarda_pai=None, ativo=True)

    def visitar_DeclaracaoVariavelNode(self, n):
        if n.nome in self.vars_dados:
            raise TraducaoErro(f"variável '{n.nome}' declarada duas vezes")

        if n.tipo == "bool":
            dominio = "boolean"
        elif n.tipo == "int":
            dominio = f"{n.range_min}..{n.range_max}"
        elif n.tipo == "enum":
            dominio = "{" + ", ".join(n.valores_enum) + "}"
        else:
            raise TraducaoErro(f"tipo '{n.tipo}' não tem equivalente no NuSMV")

        self.vars_dados[n.nome] = (dominio, self._valor_inicial(n.valor_inicial))

    def _valor_inicial(self, v):
        # O parser devolve tipos diferentes: BooleanoNode (bool), int (int), str (enum)
        if v is None:
            return None
        if hasattr(v, "aceitar"):
            return v.aceitar(self)
        return str(v)

    def visitar_EventoNode(self, n):
        if n.nome in self.eventos:
            raise TraducaoErro(f"evento '{n.nome}' declarado duas vezes")
        self.eventos.append(n.nome)

    # ------------------------------------------------------------------
    # Estados
    # ------------------------------------------------------------------
    def tratar_nivel(self, var, estados, transicoes, guarda_pai, ativo):
        if var in self.vars_estado:
            raise TraducaoErro(f"variável de estado '{var}' duplicada")

        nivel = Nivel(var, estados, transicoes, guarda_pai, ativo)
        inicial = self._inicial(estados, var)

        valores = [e.nome for e in estados]
        if guarda_pai is not None:
            valores = ["inativo"] + valores
        self.vars_estado[var] = (valores, inicial if ativo else "inativo")

        self.pilha.append(nivel)
        for t in transicoes:
            t.aceitar(self)
        for e in estados:
            e.aceitar(self)
        self.pilha.pop()

    def visitar_EstadoNode(self, e):
        nivel = self.pilha[-1]

        for d in e.declaracoes:
            d.aceitar(self)

        self.estado_atual = e
        for i in e.internos:
            i.aceitar(self)

        if e.estados_filhos:
            ativo = nivel.ativo_inicial and e.nome == self._inicial(nivel.estados, nivel.var)
            self.tratar_nivel(f"{e.nome}_state", e.estados_filhos, e.transicoes,
                              guarda_pai=f"{nivel.var} = {e.nome}", ativo=ativo)
        elif e.transicoes:
            raise TraducaoErro(f"estado '{e.nome}' tem transições mas não tem subestados")

    def visitar_EstadoParaleloNode(self, p):
        nivel = self.pilha[-1]
        ativo = nivel.ativo_inicial and p.nome == self._inicial(nivel.estados, nivel.var)
        for r in p.regioes:
            self.ctx_regiao = (f"{nivel.var} = {p.nome}", ativo)
            r.aceitar(self)

    def visitar_RegiaoNode(self, r):
        guarda_pai, ativo = self.ctx_regiao
        self.tratar_nivel(f"{r.nome}_state", r.estados, r.transicoes,
                          guarda_pai=guarda_pai, ativo=ativo)

    # ------------------------------------------------------------------
    # Transições
    # ------------------------------------------------------------------
    def visitar_TransicaoNode(self, t):
        nivel = self.pilha[-1]
        for nome in (t.origem, t.destino):
            if nome not in nivel.por_nome:
                raise TraducaoErro(f"estado '{nome}' não existe em '{nivel.var}'")
        origem = nivel.por_nome[t.origem]
        destino = nivel.por_nome[t.destino]

        cond = self._condicao(nivel, t.origem, t.evento, t.condicao)

        # 1) variáveis de estado: sai da origem, muda o nível, entra no destino
        #    (o que vem depois sobrescreve: isso trata também o auto-laço de compostos)
        novos = {}
        novos.update(self._saida(origem))
        novos[nivel.var] = t.destino
        novos.update(self._entrada(destino))
        for var, valor in novos.items():
            self.casos_estado[var].append((cond, valor))

        # 2) variáveis de dados: exit da origem -> ação da transição -> entry do destino
        acoes = list(getattr(origem, "exit", [])) + list(t.acoes) + list(getattr(destino, "entry", []))
        self._registrar_acoes(cond, acoes)

    def visitar_TransicaoInternaNode(self, i):
        nivel = self.pilha[-1]
        cond = self._condicao(nivel, self.estado_atual.nome, i.evento, i.condicao)
        self._registrar_acoes(cond, i.acoes)

    def visitar_AtribuicaoNode(self, a):
        return (a.identificador, a.expressao.aceitar(self))

    def _registrar_acoes(self, cond, acoes):
        # cada variável recebe UM caso; se for atribuída mais de uma vez, vale a última
        ultimo = dict(a.aceitar(self) for a in acoes)
        for var, expr in ultimo.items():
            self.casos_dados[var].append((cond, expr))

    def _condicao(self, nivel, origem, evento, guarda):
        """Devolve a condição como lista de conjuntos (unidos por '&' na saída)."""
        partes = []
        if nivel.guarda_pai:
            partes.append(nivel.guarda_pai)
        partes.append(f"{nivel.var} = {origem}")
        if evento:
            if evento not in self.eventos:
                raise TraducaoErro(f"evento '{evento}' não foi declarado")
            partes.append(f"event = {evento}")
        if guarda is not None:
            txt = guarda.aceitar(self)
            partes.append(txt if txt.startswith("(") else f"({txt})")
        return partes

    # ------------------------------------------------------------------
    # Auxiliares sobre a hierarquia (funções puras sobre a AST)
    # ------------------------------------------------------------------
    def _inicial(self, estados, onde):
        marcados = [e.nome for e in estados if getattr(e, "inicial", False)]
        if len(marcados) == 1:
            return marcados[0]
        if not marcados and len(estados) == 1:
            return estados[0].nome
        raise TraducaoErro(f"'{onde}' precisa ter exatamente um estado 'initial'")

    def _filhos(self, estado):
        """[(variável, lista de estados)] dos níveis logo abaixo de 'estado'."""
        if isinstance(estado, EstadoNode) and estado.estados_filhos:
            return [(f"{estado.nome}_state", estado.estados_filhos)]
        if isinstance(estado, EstadoParaleloNode):
            return [(f"{r.nome}_state", r.estados) for r in estado.regioes]
        return []

    def _entrada(self, estado):
        """Variáveis descendentes -> estado inicial (ao entrar em 'estado')."""
        r = {}
        for var, filhos in self._filhos(estado):
            ini = self._inicial(filhos, var)
            r[var] = ini
            for f in filhos:
                if f.nome == ini:
                    r.update(self._entrada(f))
        return r

    def _saida(self, estado):
        """Variáveis descendentes -> 'inativo' (ao sair de 'estado')."""
        r = {}
        for var, filhos in self._filhos(estado):
            r[var] = "inativo"
            for f in filhos:
                r.update(self._saida(f))
        return r

    # ------------------------------------------------------------------
    # Expressões: cada visitar_* devolve o TEXTO em sintaxe NuSMV
    # ------------------------------------------------------------------
    def visitar_ExpressaoBinariaNode(self, n):
        op = self.OPERADORES.get(n.operador, n.operador)
        return f"({n.esquerda.aceitar(self)} {op} {n.direita.aceitar(self)})"

    def visitar_ExpressaoUnariaNode(self, n):
        op = self.OPERADORES.get(n.operador, n.operador)
        return f"({op}{n.operando.aceitar(self)})"

    def visitar_IdentificadorNode(self, n):
        return n.nome

    def visitar_NumeroNode(self, n):
        return str(n.valor)

    def visitar_BooleanoNode(self, n):
        return "TRUE" if n.valor else "FALSE"

    # ------------------------------------------------------------------
    # Saída
    # ------------------------------------------------------------------
    def montar_saida(self):
        for var in self.casos_dados:
            if var not in self.vars_dados:
                raise TraducaoErro(f"variável '{var}' é atribuída mas não foi declarada")

        L = []
        L += ["MODULE main", "", "IVAR",
                f"    event : {{{', '.join(self.eventos)}}};", "", "VAR"]
        for var, (valores, _) in self.vars_estado.items():
            L.append(f"    {var} : {{{', '.join(valores)}}};")
        for nome, (dominio, _) in self.vars_dados.items():
            L.append(f"    {nome} : {dominio};")

        L += ["", "ASSIGN"]
        for var, (_, ini) in self.vars_estado.items():
            L.append(f"    init({var}) := {ini};")
        for nome, (_, ini) in self.vars_dados.items():
            if ini is not None:
                L.append(f"    init({nome}) := {ini};")

        for var in self.vars_estado:
            L += self._bloco_next(var, self.casos_estado[var])
        for nome in self.vars_dados:
            L += self._bloco_next(nome, self.casos_dados[nome])

        return "\n".join(L) + "\n"

    def _bloco_next(self, var, casos):
        L = ["", f"    next({var}) :=", "        case"]
        for partes, resultado in casos:
            L.append("            " + " &\n            ".join(partes) + " :")
            L.append(f"                {resultado};")
            L.append("")
        L += ["            TRUE :", f"                {var};", "        esac;"]
        return L
