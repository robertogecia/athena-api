#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lint de citações jurisprudenciais para o build de petições (peticao-rg).

Regra da casa: "nunca cite jurisprudência de memória". Este módulo torna
isso uma propriedade do build, não de disciplina: toda citação de julgado
que aparece no texto da peça (número CNJ, REsp/AREsp/RE/HC..., Tema,
Súmula, IRDR) precisa de uma FICHA verificada em "precedentes", e o que a
peça afirma sobre o julgado (relator, data, órgão, trecho transcrito) é
conferido contra a ficha.

Erros reais que motivaram cada checagem (set/2026):
  - relator de OUTRA decisão do mesmo número (um número CNJ pode ter três
    acórdãos: original, embargos, 2º embargos)     -> relator × ficha
  - data e resultado errados de um precedente       -> data × ficha
  - tese de repetitivo parafraseada além do fixado   -> literalidade
  - REsp real citado com conteúdo que não é dele     -> ficha obrigatória
  - corte em transcrição literal sem [...]           -> literalidade por segmento
  - câmara do CADASTRO do TJRO copiada para a ficha ("3ª Câmara Cível" no
    lugar da 1ª ou da 2ª, em 4 peças reais, 14/09/2026) -> 3ª Câmara Cível
    do TJRO só passa com "orgao_fonte": "fecho" na ficha

Uso:
    python3 lint_citacoes.py entrada.json    # imprime relatório; exit 2 se houver erro
    python3 lint_citacoes.py --selftest      # testes offline, sem arquivo

De dentro do build:  lint(cfg, base_dir=...) -> Relatorio (erros, avisos, resumo)

Campos opcionais na raiz do JSON da peça:
  "precedentes"             lista de fichas OU caminho de JSON com a lista
  "processos_do_caso"       números CNJ do PRÓPRIO caso (fora do lint; o número
                            de todo bloco "processo" entra sozinho nessa lista)
  "ignorar_citacoes"        chaves a ignorar pontualmente (ex.: ["Tema 3"])
  "permitir_nao_verificado" true -> todo ERRO vira AVISO e o build continua

Esquema da ficha: ver SKILL.md, seção "Citações verificadas (lint obrigatório)".
"""
import datetime
import json
import os
import re
import sys
import unicodedata
import urllib.parse
from dataclasses import dataclass, field

# Sinônimos aceitos na LEITURA (fichas antigas do vault e do segundo-cerebro).
# Quem escreve ficha nova usa só o nome canônico — ver SKILL.md.
SINONIMOS = {
    "chave": ("classe_numero",),
    "id_documento": ("doc_id",),
    "julgamento": ("data_julgamento",),
    "publicacao": ("data_publicacao",),
    "orgao": ("orgao_julgador",),
    "overruling_status": ("superacao", "status"),
    "link": ("url",),
}


def ler_campo(dados, canonico):
    """Valor de um campo da ficha, aceitando os sinônimos antigos.

    Precedência: o nome CANÔNICO vence. Ficha que traz os dois com valores
    diferentes (migração pela metade) usa o canônico e ignora o legado em
    silêncio — o inverso faria uma correção nova ser sobrescrita por um campo
    velho esquecido no arquivo.
    """
    v = dados.get(canonico)
    if v:
        return v
    for alt in SINONIMOS.get(canonico, ()):
        v = dados.get(alt)
        if v:
            return v
    return None


VERIFICACAO_PLENA = ("inteiro teor lido", "tese oficial lida")
VERIFICACAO_PARCIAL = "só ementa/índice"
VERIFICACAO_NULA = "não conferido"
VERIFICACOES = VERIFICACAO_PLENA + (VERIFICACAO_PARCIAL, VERIFICACAO_NULA)
DIAS_VALIDADE_FICHA = 180


# ---------------------------------------------------------------- normalização

def _norm_char(c):
    d = unicodedata.normalize("NFKD", c)
    base = "".join(ch for ch in d if not unicodedata.combining(ch))
    cand = base if len(base) == 1 else c
    low = cand.lower()
    return low if len(low) == 1 else cand


def normalizar(texto):
    """Minúsculas e sem acento, com o MESMO comprimento do original (1 char
    -> 1 char): os offsets casados na versão normalizada valem no original."""
    return "".join(_norm_char(c) for c in texto)


def sem_acento(s):
    return "".join(ch for ch in unicodedata.normalize("NFKD", s)
                   if not unicodedata.combining(ch))


def norm_literal(s):
    """Forma canônica para conferir literalidade: sem marcação **/*/__, sem
    acento, minúsculas, só letras/dígitos/espaços (aspas, travessões e
    pontuação não contam), espaços colapsados."""
    s = s.replace("**", "").replace("__", "").replace("*", "")
    s = sem_acento(s).lower()
    s = re.sub(r"[^a-z0-9]+", " ", s)
    return s.strip()


def _so_digitos(s):
    return re.sub(r"\D", "", s or "")


# ------------------------------------------------------------------- extrator

@dataclass
class Citacao:
    classe: str          # cnj, resp, aresp, eresp, re, are, hc, rhc, ms, rms,
                         # tema, sumula, sumula-vinculante, irdr, e a sigla de
                         # acórdão de Tribunal de Contas em minúsculo sem hífen
                         # (apltc, ac1tc, ac2rtc... — ver _RE_TC)
    numero: str          # só dígitos
    chave: str           # como apareceu no texto (para mensagens)
    inicio: int = 0
    fim: int = 0

    @property
    def ident(self):
        return (self.classe, self.numero)


_PREFIXOS = [
    "embargos de declaracao nos", "embargos de declaracao no",
    "agravo regimental nos", "agravo regimental no",
    "agravo interno nos", "agravo interno no",
    "agint nos", "agint no", "agrg nos", "agrg no", "edcl nos", "edcl no",
]
_BASES = [
    ("embargos de divergencia em recurso especial", "eresp"),
    ("agravo em recurso extraordinario", "are"),
    ("agravo em recurso especial", "aresp"),
    ("recurso extraordinario", "re"),
    ("recurso especial", "resp"),
    ("mandado de seguranca", "ms"),
    ("habeas corpus", "hc"),
    ("eresp", "eresp"), ("aresp", "aresp"), ("resp", "resp"),
    ("rhc", "rhc"), ("rms", "rms"), ("are", "are"),
    ("re", "re"), ("hc", "hc"), ("ms", "ms"),
]
_BASE_POR_TEXTO = dict(_BASES)
# siglas curtas que também são palavra/abreviação comum ("a ré 99 Tecnologia",
# "MS" de Mato Grosso do Sul): só contam se vierem EXATAMENTE em caixa-alta
# e sem acento no texto original.
_SIGLAS_ESTRITAS = {"RE", "ARE", "HC", "RHC", "MS", "RMS"}

_NUM = r"(?:n\.?[oº]?\.?|num\.?|numero)?"
_RE_STJ = re.compile(
    r"\b(?:(?:%s)\s+)*(%s)\b\.?\s*%s\s*(\d[\d.]*)"
    % ("|".join(re.escape(p) for p in _PREFIXOS),
       "|".join(re.escape(b) for b, _ in _BASES), _NUM))
_RE_CNJ = re.compile(r"\b\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}\b")
_RE_TEMA = re.compile(
    r"\btemas?\s+(?:repetitivos?\s+|de\s+repercussao\s+geral\s+)?(?:%s\s*)?"
    r"(\d{1,2}\.\d{3}|\d{1,4})\b" % _NUM)
_RE_SUMULA = re.compile(
    r"\bsumulas?\s+(vinculantes?\s+)?(?:%s\s*)?(\d{1,4})\b" % _NUM)
_RE_IRDR = re.compile(r"\birdr\s+(?:%s\s*)?(\d{1,4})\b" % _NUM)
# Acórdão de Tribunal de Contas (14/09/2026 — TCE-RO tem MCP próprio, mas a forma sigla+
# número é comum a TCs/TCU). Siglas REAIS vistas na base do TCE-RO (amostra de 1.689
# decisões, 13/09/2026): APL-TC, AC1-TC, AC2-TC, APLR-TC, AC1R-TC, AC2R-TC — abreviação
# de 2-4 letras + dígito opcional + "R" opcional (revisão) + "-TC"; número no formato
# NNNNN/AA. Sigla fora desse desenho (de outro TC/TCU que não use "-TC") não é
# reconhecida — mesma limitação de qualquer citação que este extrator não conhece:
# silenciosamente sem ficha/link, nunca erro fabricado.
_RE_TC = re.compile(r"\b([a-z]{2,4}\d?r?-tc)\.?\s*%s\s*(\d{4,6}/\d{2,4})\b" % _NUM)


def extrair_citacoes(texto):
    """Devolve as citações encontradas em `texto`, ordenadas por posição e
    sem sobreposição. A identidade de cada uma é (classe-base, dígitos)."""
    if not texto:
        return []
    norm = normalizar(texto)
    achados = []

    for m in _RE_CNJ.finditer(norm):
        achados.append(Citacao("cnj", _so_digitos(m.group(0)), texto[m.start():m.end()],
                               m.start(), m.end()))
    for m in _RE_STJ.finditer(norm):
        base = _BASE_POR_TEXTO[m.group(1)]
        if base in ("re", "are", "hc", "rhc", "ms", "rms"):
            if texto[m.start(1):m.end(1)] not in _SIGLAS_ESTRITAS:
                continue
        fim = m.end()
        while fim > m.start() and texto[fim - 1] == ".":
            fim -= 1
        digitos = _so_digitos(m.group(2))
        if not digitos:
            continue
        achados.append(Citacao(base, digitos, texto[m.start():fim], m.start(), fim))
    for m in _RE_TEMA.finditer(norm):
        achados.append(Citacao("tema", _so_digitos(m.group(1)), texto[m.start():m.end()],
                               m.start(), m.end()))
    for m in _RE_SUMULA.finditer(norm):
        classe = "sumula-vinculante" if m.group(1) else "sumula"
        achados.append(Citacao(classe, m.group(2), texto[m.start():m.end()],
                               m.start(), m.end()))
    for m in _RE_IRDR.finditer(norm):
        achados.append(Citacao("irdr", m.group(1), texto[m.start():m.end()],
                               m.start(), m.end()))
    for m in _RE_TC.finditer(norm):
        # classe leva a sigla (apltc, ac1tc...) — números repetem entre siglas
        # diferentes no mesmo ano (AC1-TC 00055/26 != APL-TC 00055/26).
        sigla = re.sub(r"[^a-z0-9]", "", m.group(1))
        achados.append(Citacao(sigla, _so_digitos(m.group(2)), texto[m.start():m.end()],
                               m.start(), m.end()))

    achados.sort(key=lambda c: (c.inicio, -(c.fim - c.inicio)))
    saida = []
    for c in achados:
        if saida and c.inicio < saida[-1].fim:
            continue
        saida.append(c)
    return saida


def parsear_chave(chave):
    """Identidade (classe, dígitos) de uma chave de ficha/ignorar, ou None."""
    cits = extrair_citacoes(chave or "")
    return cits[0].ident if cits else None


# ------------------------------------------------------------------- janelas

# abreviações que NÃO encerram frase quando seguidas de ponto
_ABREV = set("""rel rela min mina des desa art arts n no nos num p pp fl fls
inc al dje dj dou ed ex obs cf cfr vol cit op ac proc ap ag ai dr dra sr sra
srs prof pub publ julg etc ltda cia me epp adv exmo exma ilmo ilma sec seg id
ids ref reg res nr par caput jan fev mar abr mai jun jul ago set out nov dez
""".split())
_ROMANOS = re.compile(r"^(?=[ivx])m{0,3}(cm|cd|d?c{0,3})(xc|xl|l?x{0,3})(ix|iv|v?i{0,3})$")


def dividir_frases(texto):
    """Lista de (inicio, fim) das frases de `texto`. Não corta em "Rel.",
    "Min.", "j.", "art.", "n.", iniciais e números — o feijão com arroz de
    uma atribuição de julgado."""
    norm = normalizar(texto)
    limites = [0]
    for m in re.finditer(r"[.!?]+[\"”’)\]]*[ \t]+|\n+", norm):
        pos = m.end()
        if pos >= len(norm):
            break
        if "\n" in m.group(0) or m.group(0)[0] in "!?":
            limites.append(pos)
            continue
        # é um ponto: só encerra frase se vier algo "de início de frase" e se
        # o token anterior não for abreviação/inicial/numeral romano/número curto
        prox = texto[pos]
        if not (prox.isupper() or prox.isdigit() or prox in "\"“(['‘"):
            continue
        tok = re.search(r"([a-z0-9]+)[\"”’)\]]*\.", norm[:m.start() + 1])
        tok = tok.group(1) if tok else ""
        if (tok in _ABREV or len(tok) == 1 or _ROMANOS.match(tok)
                or (tok.isdigit() and len(tok) <= 2)):
            continue
        limites.append(pos)
    limites.append(len(texto))
    frases = []
    for a, b in zip(limites, limites[1:]):
        if texto[a:b].strip():
            frases.append((a, b))
    return frases or [(0, len(texto))]


def _grupo_parenteses(texto, inicio, fim):
    """(p0, p1) do grupo de parênteses mais interno que contém [inicio, fim),
    procurando o fechamento até 800 chars adiante; ou None."""
    pilha = []
    for i in range(max(0, inicio - 800), inicio):
        if texto[i] == "(":
            pilha.append(i)
        elif texto[i] == ")" and pilha:
            pilha.pop()
    if not pilha:
        return None
    p0 = pilha[-1]
    nivel = 0
    for j in range(fim, min(len(texto), fim + 800)):
        if texto[j] == "(":
            nivel += 1
        elif texto[j] == ")":
            if nivel == 0:
                return (p0 + 1, j)
            nivel -= 1
    return None


def janelas(texto, citacoes, inteiro=False):
    """Para cada citação, (inicio, fim) da janela onde relator/data/órgão são
    procurados: o grupo de parênteses que a contém, senão a frase; com
    `inteiro`, o texto todo (atribuição de bloco `citacao`). Quando o mesmo
    contêiner tem várias citações, cada uma fica com o trecho que vai dela
    até a próxima (a primeira herda também o começo do contêiner)."""
    if not citacoes:
        return []
    frases = dividir_frases(texto) if not inteiro else [(0, len(texto))]
    conts = []
    for c in citacoes:
        grupo = None if inteiro else _grupo_parenteses(texto, c.inicio, c.fim)
        if grupo:
            conts.append(grupo)
            continue
        cont = frases[-1]
        for f in frases:
            if f[0] <= c.inicio < f[1]:
                cont = f
                break
        conts.append(cont)
    saida = []
    for i, c in enumerate(citacoes):
        c0, c1 = conts[i]
        irmaos = [j for j in range(len(citacoes)) if conts[j] == conts[i]]
        k = irmaos.index(i)
        ini = c0 if k == 0 else c.inicio
        fim = c1 if k == len(irmaos) - 1 else citacoes[irmaos[k + 1]].inicio
        saida.append((ini, fim))
    return saida


# --------------------------------------------------------------------- fichas

@dataclass
class Ficha:
    dados: dict
    ident: tuple

    @property
    def chave(self):
        return ler_campo(self.dados, "chave") or self.dados.get("numero") or "?"

    @property
    def verificacao(self):
        v = (self.dados.get("verificacao") or VERIFICACAO_NULA)
        return sem_acento(str(v)).strip().lower()

    @property
    def plena(self):
        return self.verificacao in tuple(sem_acento(x) for x in VERIFICACAO_PLENA)

    @property
    def nula(self):
        return self.verificacao == sem_acento(VERIFICACAO_NULA)

    def texto_literal(self):
        partes = [self.dados.get(k) for k in ("trecho", "dispositivo", "tese", "ementa")]
        return " ".join(str(p) for p in partes if p)

    def datas(self):
        """Datas conhecidas da ficha em (dia, mês, ano)."""
        saida = []
        for k in ("julgamento", "publicacao"):
            v = ler_campo(self.dados, k)
            if not v:
                continue
            m = re.match(r"(\d{4})-(\d{2})-(\d{2})", str(v))
            if m:
                saida.append((int(m.group(3)), int(m.group(2)), int(m.group(1))))
                continue
            m = re.match(r"(\d{1,2})[/.-](\d{1,2})[/.-](\d{4})", str(v))
            if m:
                saida.append((int(m.group(1)), int(m.group(2)), int(m.group(3))))
        return saida

    def relatores(self):
        return [str(self.dados.get(k)) for k in ("relator", "relator_para_acordao")
                if self.dados.get(k)]


def carregar_fichas(cfg, base_dir="."):
    """Dict ident -> Ficha a partir de cfg["precedentes"] (lista ou caminho)."""
    prec = cfg.get("precedentes")
    avisos = []
    if isinstance(prec, str):
        caminho = prec if os.path.isabs(prec) else os.path.join(base_dir, prec)
        with open(caminho, encoding="utf-8") as f:
            prec = json.load(f)
        if isinstance(prec, dict) and "precedentes" in prec:
            prec = prec["precedentes"]
    prec = prec or []
    if not isinstance(prec, list):
        raise ValueError('"precedentes" deve ser uma lista de fichas ou o caminho de um JSON com essa lista')
    fichas = {}
    for i, d in enumerate(prec):
        if not isinstance(d, dict):
            avisos.append("precedentes[%d] não é um objeto; ignorado" % i)
            continue
        ident = parsear_chave(str(ler_campo(d, "chave") or ""))
        if ident is None:
            dig = _so_digitos(str(d.get("numero") or ""))
            if len(dig) == 20:
                ident = ("cnj", dig)
            else:
                ident = parsear_chave(str(d.get("numero") or ""))
        if ident is None:
            avisos.append('ficha %d ("%s"): chave não reconhecida — use classe + número '
                          '(ex.: "REsp 1.959.812", "Tema 1265", "AI 0819477-50.2024.8.22.0000")'
                          % (i + 1, d.get("chave") or d.get("numero") or "?"))
            continue
        if ident in fichas:
            avisos.append('ficha duplicada para "%s": a última prevalece' % (d.get("chave") or ident[1]))
        fichas[ident] = Ficha(d, ident)
    return fichas, avisos


# ------------------------------------------------------------------- checagens

_TITULOS = {"desembargador", "desembargadora", "juiz", "juiza", "convocado", "convocada",
            "ministro", "ministra", "relator", "relatora", "substituto", "substituta",
            "redator", "redatora", "acordao", "para", "min", "des", "rel", "desa"}


def sobrenomes(nome):
    return [w for w in re.split(r"[^a-z]+", sem_acento(nome).lower())
            if len(w) >= 4 and w not in _TITULOS]


_RE_REL = re.compile(
    r"(?:\brel\.?|\brelator(?:a)?\.?|\bredator(?:a)?\.?)\s*:?\s*(?:p/?\.?\s*(?:o\s*)?acordao\s*:?\s*)?"
    r"(?:min\.?|ministr[oa]|des[a.]*\.?|desembargador(?:a)?|juiz(?:a)?(?:\s+convocad[oa])?)?\.?\s*"
    r"([^,;()\n]{3,80}?)(?=\s*(?:,|;|\)|$|\s+j\.|\s+julg|\s+dj|\s+data|\s+publ))",
    re.I)
_RE_DATA = re.compile(r"\b(\d{1,2})[/.-](\d{1,2})[/.-](\d{4})\b")
_RE_ORGAO = re.compile(r"\b(\d{1,2})\s*[ªa°º]?\s*(camara|turma|secao|seção)\b", re.I)


def _relator_no_texto(janela_norm, janela_orig):
    m = _RE_REL.search(janela_norm)
    if not m:
        return None
    return janela_orig[m.start(1):m.end(1)].strip()


def _orgao(texto_norm):
    m = _RE_ORGAO.search(texto_norm)
    return (int(m.group(1)), m.group(2).replace("ç", "c")) if m else None


# O cadastro do portal do TJRO põe na "3ª Câmara Cível" acórdãos julgados pela 1ª
# ou pela 2ª (medição de 14/09/2026: 15 de 24 processos), e a ficha que copia o
# cadastro passa limpa na conferência peça × ficha — foi assim em 4 peças reais.
# A câmara que vale é a do fecho do acórdão ("acordam os Magistrados da(o) ...").
_RE_3A_CIVEL = re.compile(r"\b3\s*a?\s*camara\s+civel\b")


def _eh_tjro(c, ficha):
    if c.classe == "cnj" and len(c.numero) == 20 and c.numero[13:16] == "822":
        return True
    trib = sem_acento(str(ler_campo(ficha.dados, "tribunal") or "")).lower()
    return re.sub(r"[^a-z]", "", trib) == "tjro"


# ------------------------------------------------------------ links oficiais
# Pedido do usuário (14/09/2026): a peça gerada leva link para o inteiro teor
# oficial de cada julgado citado, para o juiz clicar e conferir a fonte. O link
# vem do campo `link` da ficha e só entra na peça se for de domínio público
# brasileiro (tribunais .jus.br, tribunais de contas .tc.br e .gov.br — o TCU e
# vários TCEs estão em .gov.br —, legislativo .leg.br, MP .mp.br), do HOST do
# próprio tribunal citado quando o escritório tem MCP para ele (TJRO, TCE-RO — ver
# `_HOSTS_POR_TRIBUNAL`: link do JURIS numa ficha do TCE-RO, ou vice-versa, é erro
# mesmo os dois sendo domínio oficial) e, no JURIS do TJRO, se abrir a MESMA peça da
# ficha (`id=` igual ao `id_documento`): uma ficha real apontava para o relatório de
# outro julgamento sob o mesmo número, e o juiz cairia no documento errado. Agregador
# (JusRatio, Jusbrasil) fica de fora: o juiz não abre, ou não é fonte.
DOMINIOS_OFICIAIS = (".jus.br", ".tc.br", ".gov.br", ".leg.br", ".mp.br")


def link_oficial(url):
    try:
        u = urllib.parse.urlsplit(str(url or "").strip())
    except ValueError:
        return False
    host = (u.hostname or "").lower()
    return u.scheme in ("http", "https") and host.endswith(DOMINIOS_OFICIAIS)


def id_no_link_juris(url):
    """Valor de `id=` num link do JURIS/TJRO (a peça que o link abre), ou None."""
    try:
        u = urllib.parse.urlsplit(str(url or "").strip())
    except ValueError:
        return None
    if (u.hostname or "").lower() != "juris.tjro.jus.br":
        return None
    v = urllib.parse.parse_qs(u.query).get("id")
    return v[0].strip() if v else None


# Host esperado por tribunal com MCP próprio — pega o erro de colar o link de UM
# tribunal na ficha de OUTRO (ex.: link do JURIS/TJRO numa ficha "tribunal": "TCE-RO"),
# que `link_oficial` sozinho não pega: os dois domínios são igualmente ".jus.br"/
# ".tc.br", oficiais os dois, só que do tribunal errado. Escopo deliberadamente restrito
# aos tribunais cujo host de link já foi confirmado ao vivo por este escritório — TRF1
# fica de fora de propósito: o portal do CJF devolve link genérico de consulta pública
# para caso PJe (sem número), então um host único não bastaria para separar "link certo"
# de "link só apontando para a consulta" (ver README do MCP TRF1, teto de verificação).
_HOSTS_POR_TRIBUNAL = {
    "tjro": ("juris.tjro.jus.br",),
    "tcero": ("tcero.tc.br", "tce.ro.gov.br"),  # tce.ro.gov.br: host antigo, ainda existe (301)
}


def _tribunal_normalizado(dados):
    """"TCE-RO" -> "tcero", "TJRO" -> "tjro" — mesmo padrão de fold do resto do arquivo."""
    trib = sem_acento(str(ler_campo(dados, "tribunal") or "")).lower()
    return re.sub(r"[^a-z]", "", trib) or None


def host_errado_para_tribunal(dados, url):
    """None se o host do link é compatível com o tribunal da ficha (ou o tribunal não
    está no escopo do check); senão, o texto do erro."""
    trib = _tribunal_normalizado(dados)
    hosts = _HOSTS_POR_TRIBUNAL.get(trib)
    if not hosts:
        return None
    try:
        host = (urllib.parse.urlsplit(str(url or "").strip()).hostname or "").lower()
    except ValueError:
        return None
    if host in hosts or any(host.endswith("." + h) for h in hosts):
        return None
    return ('link de domínio de outro tribunal (%s) numa ficha "%s": use o link do '
            'próprio %s (%s)' % (host, ler_campo(dados, "tribunal"), ler_campo(dados, "tribunal"),
                                  " ou ".join(hosts)))


def problema_do_link(dados):
    """None se o link da ficha pode ir para a peça; senão ("aviso"|"erro", texto)."""
    lk = str(ler_campo(dados, "link") or "").strip()
    if not re.match(r"https?://", lk, re.I):  # vazio ou marcador ("PENDENTE: abrir o acórdão")
        return ("aviso", "sem link do inteiro teor: a peça sai sem link para este julgado")
    if not link_oficial(lk):
        return ("aviso", "link fora de portal oficial (%s): não vai para a peça — use o do tribunal" % lk[:60])
    trib_prob = host_errado_para_tribunal(dados, lk)
    if trib_prob:
        return ("erro", trib_prob)
    id_link = id_no_link_juris(lk)
    # Ids de peça do JURIS citados no id_documento. Fichas antigas guardam ali o número
    # CNJ ou uma lista ("36456829 (acórdão); 36456832 (ementa)"): o CNJ não é id de
    # peça e não se compara; na lista, basta o link abrir uma das peças listadas.
    ids_ficha = set(re.findall(r"(?<![\d.\-])\d{6,10}(?![\d.\-])", str(ler_campo(dados, "id_documento") or "")))
    if id_link and ids_ficha and id_link not in ids_ficha:
        return ("erro", "o link abre outro documento do JURIS (id %s), não a peça da ficha (id %s): "
                        "copie o link da mesma peça no MCP do TJRO" % (id_link, ", ".join(sorted(ids_ficha))))
    # LIMITE ESTRUTURAL (14/09/2026): o link do PDF do TCE-RO é um hash opaco
    # (`AbrirPdfConvidado/<hash>`) — não carrega o id da decisão como o JURIS carrega
    # `?id=`, então não há como este lint confirmar que o link abre a MESMA decisão da
    # ficha (só o host_errado_para_tribunal acima, que pega tribunal errado, não decisão
    # errada dentro do mesmo tribunal). A proteção contra link da decisão errada sob o
    # mesmo número de acórdão do TCE-RO é só disciplina de quem monta a ficha: sempre
    # `obter_acordao_tcero(id_decisao=<id específico>)`, nunca copiar link de uma busca
    # por número que trouxe mais de uma decisão.
    return None


def carregar_links(cfg, base_dir="."):
    """ident -> url para as fichas cujo link pode ir para a peça (ver problema_do_link)."""
    try:
        fichas, _ = carregar_fichas(cfg, base_dir)
    except (OSError, ValueError, json.JSONDecodeError):
        return {}
    return {ident: str(ler_campo(f.dados, "link")).strip()
            for ident, f in fichas.items()
            if not f.nula and problema_do_link(f.dados) is None}


def _expandir_parenteses(texto, inicio, fim):
    """(a, b), PARÊNTESES INCLUÍDOS, do grupo "(...)" que envolve [inicio, fim);
    ou None se a citação não estiver dentro de um grupo. Reaproveita
    `_grupo_parenteses` (mesmo algoritmo da janela peça×ficha), que devolve o
    miolo sem os parênteses — aqui eles entram, porque o link cobre a
    referência visível inteira, parênteses inclusos."""
    grp = _grupo_parenteses(texto, inicio, fim)
    return (grp[0] - 1, grp[1] + 1) if grp else None


def segmentar_links(texto, links):
    """[(trecho, url ou None)]: cada citação que tem link vira um trecho próprio.

    Pedido do usuário (14/09/2026): a referência inteira entre parênteses —
    "(TJRO, Agravo de Instrumento NNNNNNN-NN.AAAA.8.22.0000, 1ª Câmara Cível,
    Rel. ..., j. .../.../....)" — vira o link, não só o número. Quando a
    citação está dentro de um grupo "(...)" que a contém SOZINHA (nenhuma outra
    citação com link no mesmo grupo — ex.: duas citações no mesmo parêntese,
    separadas por ";"), o link cobre o grupo inteiro; do contrário, cada
    citação linka só o seu próprio número, para não apontar um mesmo trecho
    para dois lugares diferentes. Fora de parênteses (citação solta no texto
    corrido), linka só o número, como antes.
    """
    if not texto or not links:
        return [(texto, None)]
    citas = extrair_citacoes(texto)
    if not citas:
        return [(texto, None)]
    por_grupo = {}
    alvos = []  # (inicio, fim, url), sem sobreposição
    for c in citas:
        url = links.get(c.ident)
        if not url:
            continue
        grp = _expandir_parenteses(texto, c.inicio, c.fim)
        if grp:
            por_grupo.setdefault(grp, []).append(url)
        else:
            alvos.append((c.inicio, c.fim, url))
    for (p0, p1), urls in por_grupo.items():
        alvos.append((p0, p1, urls[0]) if len(urls) == 1 else None)
    alvos = [a for a in alvos if a]
    # Duas citações do MESMO grupo (>1 url) não expandem; cada uma perde a
    # entrada acima e volta a linkar só o próprio número.
    cobertos = {(p0, p1) for (p0, p1), urls in por_grupo.items() if len(urls) > 1}
    if cobertos:
        for c in citas:
            url = links.get(c.ident)
            grp = _expandir_parenteses(texto, c.inicio, c.fim) if url else None
            if url and grp in cobertos:
                alvos.append((c.inicio, c.fim, url))
    alvos.sort()
    saida, pos = [], 0
    for ini, fim, url in alvos:
        if ini < pos:
            continue  # sobreposição residual: mantém o primeiro, ignora o resto
        if ini > pos:
            saida.append((texto[pos:ini], None))
        saida.append((texto[ini:fim], url))
        pos = fim
    if pos < len(texto):
        saida.append((texto[pos:], None))
    return saida or [(texto, None)]


@dataclass
class Relatorio:
    erros: list = field(default_factory=list)
    avisos: list = field(default_factory=list)
    n_citacoes: int = 0
    n_com_ficha: int = 0
    n_sem_ficha: int = 0
    n_inconsistentes: int = 0
    rebaixado: bool = False

    @property
    def resumo(self):
        return ("Lint de citações: %d citação(ões), %d com ficha, %d sem ficha, "
                "%d inconsistente(s), %d aviso(s)%s"
                % (self.n_citacoes, self.n_com_ficha, self.n_sem_ficha,
                   self.n_inconsistentes, len(self.avisos),
                   " — ERROS REBAIXADOS A AVISO por permitir_nao_verificado" if self.rebaixado else ""))

    def texto(self):
        linhas = [self.resumo]
        for e in self.erros:
            linhas.append("  ERRO: " + e)
        for a in self.avisos:
            linhas.append("  aviso: " + a)
        return "\n".join(linhas)


_CAMPOS_TEXTO = ("texto", "atribuicao", "titulo", "encerramento")
_CAMPOS_LISTA = ("itens", "colunas")
_BLOCOS_FORA = {"processo", "fecho", "enderecamento", "espaco", "quebra_pagina"}
_SEPARADOR_CORTE = re.compile(r"\[\s*(?:\.{3}|…)\s*\]|\(\s*(?:\.{3}|…)\s*\)|…|\.{3}")


def _textos_do_bloco(b):
    """(campo, texto) de tudo que é texto num bloco."""
    for k in _CAMPOS_TEXTO:
        v = b.get(k)
        if isinstance(v, str) and v.strip():
            yield k, v
    for k in _CAMPOS_LISTA:
        for i, v in enumerate(b.get(k) or []):
            if isinstance(v, str) and v.strip():
                yield "%s[%d]" % (k, i), v
    for i, linha in enumerate(b.get("linhas") or []):
        for j, v in enumerate(linha or []):
            if isinstance(v, str) and v.strip():
                yield "linhas[%d][%d]" % (i, j), v


def lint(cfg, base_dir="."):
    rel = Relatorio()
    blocks = cfg.get("blocks") or []
    try:
        fichas, avisos_fichas = carregar_fichas(cfg, base_dir)
    except (OSError, ValueError, json.JSONDecodeError) as e:
        rel.erros.append("precedentes: %s" % e)
        fichas, avisos_fichas = {}, []
    rel.avisos.extend(avisos_fichas)

    # Processos do próprio caso: fora do lint.
    do_caso = {_so_digitos(str(x)) for x in (cfg.get("processos_do_caso") or [])}
    for b in blocks:
        if isinstance(b, dict) and b.get("tipo") == "processo":
            for c in extrair_citacoes(str(b.get("texto") or "")):
                if c.classe == "cnj":
                    do_caso.add(c.numero)
    ignorar = set()
    for x in cfg.get("ignorar_citacoes") or []:
        ident = parsear_chave(str(x))
        if ident:
            ignorar.add(ident)
        else:
            rel.avisos.append('ignorar_citacoes: "%s" não é uma citação reconhecível; ignorado' % x)

    usadas = set()
    avisou_parcial = set()
    avisou_link = set()
    hoje = datetime.date.today()

    for n, b in enumerate(blocks, 1):
        if not isinstance(b, dict) or b.get("tipo") in _BLOCOS_FORA:
            continue
        tipo = b.get("tipo") or "?"
        fichas_do_bloco = []
        for campo, texto in _textos_do_bloco(b):
            cits = extrair_citacoes(texto)
            if not cits:
                continue
            inteiro = tipo == "citacao" and campo == "atribuicao"
            wins = janelas(texto, cits, inteiro=inteiro)
            norm = normalizar(texto)
            for c, (w0, w1) in zip(cits, wins):
                if c.ident in ignorar or (c.classe == "cnj" and c.numero in do_caso):
                    continue
                rel.n_citacoes += 1
                onde = "bloco %d, %s, %s" % (n, tipo, campo)
                ficha = fichas.get(c.ident)
                if ficha is None or ficha.nula:
                    rel.n_sem_ficha += 1
                    msg = 'citação sem ficha verificada: "%s" (%s)' % (c.chave, onde)
                    if ficha is not None:
                        msg += ' — a ficha existe mas está "não conferido"'
                    elif c.classe == "cnj":
                        msg += " — se for processo do próprio caso, liste em processos_do_caso"
                    rel.erros.append(msg)
                    continue
                rel.n_com_ficha += 1
                usadas.add(c.ident)
                if campo == "atribuicao":
                    fichas_do_bloco.append(ficha)
                if not ficha.plena and c.ident not in avisou_parcial:
                    avisou_parcial.add(c.ident)
                    rel.avisos.append('ficha "%s" conferida só pela ementa/índice — relator e câmara '
                                      'podem divergir do texto do acórdão' % ficha.chave)
                ve = str(ler_campo(ficha.dados, "verificado_em") or "")
                m = re.match(r"(\d{4})-(\d{2})-(\d{2})", ve)
                if m and c.ident not in avisou_parcial:
                    idade = (hoje - datetime.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))).days
                    if idade > DIAS_VALIDADE_FICHA:
                        avisou_parcial.add(c.ident)
                        rel.avisos.append('ficha "%s" verificada há %d dias — reconfirmar vigência/superação'
                                          % (ficha.chave, idade))
                # link do inteiro teor que vai para a peça (uma vez por ficha)
                if c.ident not in avisou_link:
                    avisou_link.add(c.ident)
                    prob = problema_do_link(ficha.dados)
                    if prob:
                        (rel.erros if prob[0] == "erro" else rel.avisos).append(
                            'ficha "%s": %s' % (ficha.chave, prob[1]))
                jan_orig = texto[w0:w1]
                jan_norm = norm[w0:w1]
                inconsistente = False
                # data
                datas_txt = {(int(d), int(mm), int(a)) for d, mm, a in _RE_DATA.findall(jan_orig)}
                datas_ficha = set(ficha.datas())
                if datas_txt and datas_ficha and not (datas_txt & datas_ficha):
                    inconsistente = True
                    rel.erros.append('data divergente da ficha "%s" (%s): peça diz %s; ficha: %s'
                                     % (ficha.chave, onde,
                                        ", ".join("%02d/%02d/%d" % x for x in sorted(datas_txt)),
                                        ", ".join("%02d/%02d/%d" % x for x in sorted(datas_ficha))))
                # relator
                rel_txt = _relator_no_texto(jan_norm, jan_orig)
                if rel_txt:
                    a = sobrenomes(rel_txt)
                    bset = {w for r in ficha.relatores() for w in sobrenomes(r)}
                    if a and bset and not any(w in bset for w in a):
                        inconsistente = True
                        rel.erros.append('relator divergente da ficha "%s" (%s): peça diz "%s"; ficha: %s'
                                         % (ficha.chave, onde, rel_txt, " / ".join(ficha.relatores())))
                # órgão
                org_txt = _orgao(jan_norm)
                org_ficha = _orgao(normalizar(str(ler_campo(ficha.dados, "orgao") or "")))
                if org_txt and org_ficha and org_txt != org_ficha:
                    inconsistente = True
                    rel.erros.append('órgão divergente da ficha "%s" (%s): peça diz %dª %s; ficha: %s'
                                     % (ficha.chave, onde, org_txt[0], org_txt[1], ler_campo(ficha.dados, "orgao")))
                # 3ª Câmara Cível do TJRO: só com a câmara confirmada no fecho
                fonte = sem_acento(str(ficha.dados.get("orgao_fonte") or "")).strip().lower()
                if _RE_3A_CIVEL.search(jan_norm) and _eh_tjro(c, ficha) and fonte != "fecho":
                    rel.erros.append(
                        'câmara não confirmada no fecho: "%s" (%s) é citado como 3ª Câmara Cível do TJRO, '
                        'e o cadastro do portal põe na 3ª acórdãos julgados pela 1ª ou pela 2ª (15 de 24 '
                        'processos na medição de 14/09/2026). Confira o fecho do acórdão ("acordam os '
                        'Magistrados da(o) ...") e registre "orgao_fonte": "fecho" na ficha'
                        % (ficha.chave, onde))
                if inconsistente:
                    rel.n_inconsistentes += 1

        # literalidade do que está entre aspas
        if tipo == "citacao" and fichas_do_bloco:
            base = " ".join(norm_literal(f.texto_literal()) for f in fichas_do_bloco).strip()
            chaves = ", ".join(f.chave for f in fichas_do_bloco)
            if not base:
                rel.avisos.append('bloco %d (citacao): ficha "%s" sem texto literal — literalidade não conferida'
                                  % (n, chaves))
            else:
                for seg in _SEPARADOR_CORTE.split(str(b.get("texto") or "")):
                    ns = norm_literal(seg)
                    if len(ns.split()) < 2:
                        continue
                    if ns not in base:
                        rel.n_inconsistentes += 1
                        rel.erros.append('bloco %d (citacao, "%s"): trecho entre aspas não localizado literalmente '
                                         'na ficha (paráfrase ou corte sem [...]?): «%s»'
                                         % (n, chaves, seg.strip()[:70] + ("…" if len(seg.strip()) > 70 else "")))

    for ident, f in fichas.items():
        if ident not in usadas and not f.nula:
            rel.avisos.append('ficha "%s" não é citada em nenhum bloco' % f.chave)

    if rel.erros and cfg.get("permitir_nao_verificado"):
        rel.avisos = ["(rebaixado) " + e for e in rel.erros] + rel.avisos
        rel.erros = []
        rel.rebaixado = True
    return rel


# ------------------------------------------------------------------- selftest

def _selftest():
    F = lambda **k: dict({"chave": "REsp 1.959.812", "tribunal": "STJ", "orgao": "Quarta Turma",
                          "relator": "Min. Raul Araújo", "julgamento": "2025-12-16",
                          "trecho": "cabível a fixação dos honorários sucumbenciais sobre o valor da causa",
                          "verificado_em": "2026-09-04", "verificacao": "inteiro teor lido"}, **k)
    P = lambda t: {"tipo": "paragrafo", "texto": t}

    def run(blocks, **raiz):
        cfg = {"blocks": blocks}
        cfg.update(raiz)
        return lint(cfg)

    # 1. CNJ sem ficha -> erro (com dica de processos_do_caso)
    r = run([P("Como decidiu o TJRO no AI 0819477-50.2024.8.22.0000.")])
    assert len(r.erros) == 1 and "sem ficha" in r.erros[0] and "processos_do_caso" in r.erros[0], r.erros
    # 2. com ficha -> ok
    f_ai = {"chave": "AI 0819477-50.2024.8.22.0000", "orgao": "2ª Câmara Cível", "relator": "Des. Alexandre Miguel",
            "julgamento": "2025-11-07", "trecho": "ACOLHO os presentes embargos", "verificacao": "inteiro teor lido",
            "verificado_em": "2026-09-04"}
    r = run([P("Como decidiu o TJRO (AI 0819477-50.2024.8.22.0000, Rel. Des. Alexandre Miguel, j. 07/11/2025).")],
            precedentes=[f_ai])
    assert not r.erros, r.erros
    assert r.n_com_ficha == 1
    # 3. relator trocado -> erro
    r = run([P("(AI 0819477-50.2024.8.22.0000, 2ª Câmara Cível, Rel. Des. Jorge Luiz de Moura Gurgel do Amaral, j. 07/11/2025)")],
            precedentes=[f_ai])
    assert any("relator divergente" in e for e in r.erros), r.erros
    # 4. data divergente -> erro
    r = run([P("(AI 0819477-50.2024.8.22.0000, Rel. Des. Alexandre Miguel, j. 29/04/2026)")], precedentes=[f_ai])
    assert any("data divergente" in e for e in r.erros), r.erros
    # 5. órgão divergente -> erro
    r = run([P("(AI 0819477-50.2024.8.22.0000, 1ª Câmara Cível, Rel. Des. Alexandre Miguel)")], precedentes=[f_ai])
    assert any("órgão divergente" in e for e in r.erros), r.erros
    # 6. citacao literal com [...] -> ok
    cit = {"tipo": "citacao", "texto": "cabível a fixação [...] sobre o valor da causa",
           "atribuicao": "(STJ, REsp 1.959.812, Quarta Turma, Rel. Min. Raul Araújo, j. 16/12/2025)"}
    r = run([cit], precedentes=[F()])
    assert not r.erros, r.erros
    # 7. paráfrase -> erro
    cit2 = dict(cit, texto="os honorários devem incidir sobre o valor da causa")
    r = run([cit2], precedentes=[F()])
    assert any("não localizado literalmente" in e for e in r.erros), r.erros
    # 8. Tema sem ficha -> erro
    r = run([P("Conforme o Tema 1265 do STJ, a fixação é equitativa.")])
    assert len(r.erros) == 1 and "Tema 1265" in r.erros[0], r.erros
    # 9. art./Lei não detectados
    r = run([P("Nos termos do art. 1.022 do CPC e da Lei 13.105/2015, com base no art. 85, § 8º.")])
    assert r.n_citacoes == 0 and not r.erros, (r.n_citacoes, r.erros)
    # 10. processos_do_caso e bloco processo excluem
    r = run([{"tipo": "processo", "texto": "Processo nº 0800000-00.2024.8.22.0015"},
             P("Nos autos 0800000-00.2024.8.22.0015 e no agravo 0800001-11.2026.8.22.0000 já se disse.")],
            processos_do_caso=["0800001-11.2026.8.22.0000"])
    assert r.n_citacoes == 0 and not r.erros, r.erros
    # 11. ignorar_citacoes
    r = run([P("O tema 3 da audiência foi adiado.")], ignorar_citacoes=["Tema 3"])
    assert not r.erros, r.erros
    # 12. permitir_nao_verificado rebaixa
    r = run([P("Conforme o Tema 1265 do STJ.")], permitir_nao_verificado=True)
    assert not r.erros and r.rebaixado and any("rebaixado" in a for a in r.avisos), (r.erros, r.avisos)
    # 13. só ementa/índice -> aviso, não erro
    r = run([P("(REsp 1.959.812, Rel. Min. Raul Araújo)")], precedentes=[F(verificacao="só ementa/índice")])
    assert not r.erros and any("só pela ementa" in a for a in r.avisos), (r.erros, r.avisos)
    # 14. não conferido -> sem ficha
    r = run([P("(REsp 1.959.812)")], precedentes=[F(verificacao="não conferido")])
    assert any("não conferido" in e for e in r.erros), r.erros
    # 15. REsp com pontos casa com número sem pontos
    r = run([P("(REsp 1.959.812)")], precedentes=[F(chave="REsp 1959812")])
    assert not r.erros, r.erros
    # 16. AgInt no AREsp casa pela classe-base
    r = run([P("(AgInt no AREsp 1.792.997, Rel. Min. Raul Araújo, j. 08/08/2022)")],
            precedentes=[{"chave": "AREsp 1792997", "relator": "Min. Raul Araújo", "julgamento": "2022-08-08",
                          "verificacao": "inteiro teor lido"}])
    assert not r.erros, r.erros
    # 17. ficha nunca citada -> aviso
    r = run([P("Sem citações aqui.")], precedentes=[F()])
    assert any("não é citada" in a for a in r.avisos), r.avisos
    # 18. precedentes como caminho de arquivo
    import tempfile
    d = tempfile.mkdtemp()
    caminho = os.path.join(d, "fichas.json")
    with open(caminho, "w", encoding="utf-8") as fh:
        json.dump([F()], fh)
    r = lint({"blocks": [P("(REsp 1.959.812, Rel. Min. Raul Araújo)")], "precedentes": "fichas.json"}, base_dir=d)
    assert not r.erros, r.erros
    # 19. siglas curtas só em caixa alta: "a ré 99 Tecnologia" não é RE 99
    r = run([P("A RÉ 99 Tecnologia Ltda. contestou; a ré 99 alegou prescrição.")])
    assert r.n_citacoes == 0, r.n_citacoes
    # 20. Súmula e Súmula Vinculante são chaves distintas
    r = run([P("Aplica-se a Súmula 83 do STJ e a Súmula Vinculante 10.")],
            precedentes=[{"chave": "Súmula 83", "tribunal": "STJ", "tese": "x", "verificacao": "tese oficial lida"}])
    assert len(r.erros) == 1 and "Vinculante 10" in r.erros[0], r.erros
    # 21. duas citações na mesma frase, cada uma com sua janela
    r = run([P("Nesse sentido: REsp 1.959.812, Rel. Min. Raul Araújo, j. 16/12/2025; e AREsp 1.792.997, Rel. Min. Raul Araújo, j. 08/08/2022.")],
            precedentes=[F(), {"chave": "AREsp 1792997", "relator": "Min. Raul Araújo", "julgamento": "2022-08-08",
                              "verificacao": "inteiro teor lido"}])
    assert not r.erros, r.erros
    # 22. ficha antiga (vault) com nomes sinônimos é lida igual
    antiga = {"chave": "AI 0819477-50.2024.8.22.0000", "orgao_julgador": "2ª Câmara Cível",
              "relator": "Des. Alexandre Miguel", "data_julgamento": "2025-11-07",
              "doc_id": "30009487", "superacao": "vigente", "trecho": "ACOLHO os presentes embargos",
              "verificacao": "inteiro teor lido", "verificado_em": "2026-09-04"}
    r = run([P("(AI 0819477-50.2024.8.22.0000, 2ª Câmara Cível, Rel. Des. Alexandre Miguel, j. 07/11/2025)")],
            precedentes=[antiga])
    assert not r.erros, r.erros
    # e divergência continua sendo pega com os nomes antigos
    r = run([P("(AI 0819477-50.2024.8.22.0000, 1ª Câmara Cível, Rel. Des. Alexandre Miguel, j. 29/04/2026)")],
            precedentes=[antiga])
    assert any("órgão divergente" in e for e in r.erros), r.erros
    assert any("data divergente" in e for e in r.erros), r.erros
    # 23. `classe_numero` (nome antigo do segundo-cerebro) é lido como `chave`
    r = run([P("(REsp 1.959.812, Rel. Min. Raul Araújo)")],
            precedentes=[{"classe_numero": "REsp 1.959.812", "relator": "Min. Raul Araújo",
                          "verificacao": "inteiro teor lido", "trecho": "x"}])
    assert not r.erros, r.erros
    # 24. canônico vence o sinônimo quando os dois vêm com valores diferentes
    r = run([P("(AI 0819477-50.2024.8.22.0000, Rel. Des. Alexandre Miguel, j. 07/11/2025)")],
            precedentes=[{"chave": "AI 0819477-50.2024.8.22.0000", "relator": "Des. Alexandre Miguel",
                          "julgamento": "2025-11-07", "data_julgamento": "2026-04-29",
                          "verificacao": "inteiro teor lido", "trecho": "x"}])
    assert not r.erros, r.erros  # usou 2025-11-07 (canônico), não 2026-04-29 (legado)
    # 25. 3ª Câmara Cível do TJRO sem "orgao_fonte": "fecho" -> erro; com ele -> ok (erro real, 14/09/2026)
    f3 = {"chave": "AI 0803319-80.2025.8.22.0000", "tribunal": "TJRO", "orgao": "3ª Câmara Cível",
          "relator": "Des. Isaias Fonseca Moraes", "julgamento": "2025-10-08", "trecho": "x",
          "verificacao": "inteiro teor lido", "verificado_em": "2026-09-14"}
    txt3 = "(TJRO, ED no AI 0803319-80.2025.8.22.0000, 3ª Câmara Cível, Rel. Des. Isaias Fonseca Moraes, j. 08/10/2025)"
    r = run([P(txt3)], precedentes=[f3])
    assert len(r.erros) == 1 and "não confirmada no fecho" in r.erros[0], r.erros
    r = run([P(txt3)], precedentes=[dict(f3, orgao_fonte="fecho")])
    assert not r.erros, r.erros
    # ficha já corrigida pelo fecho (2ª) contra peça que ainda diz 3ª: as duas travas falam
    r = run([P(txt3)], precedentes=[dict(f3, orgao="2ª Câmara Cível", orgao_fonte="fecho")])
    assert any("órgão divergente" in e for e in r.erros), r.erros
    # 26. a trava é só do TJRO e só da 3ª Câmara Cível
    r = run([P("(TJRO, AI 0819477-50.2024.8.22.0000, 2ª Câmara Cível, Rel. Des. Alexandre Miguel, j. 07/11/2025)")],
            precedentes=[f_ai])
    assert not r.erros, r.erros
    f_rs = {"chave": "AC 5001234-56.2024.8.21.0001", "tribunal": "TJRS", "orgao": "3ª Câmara Cível",
            "relator": "Des. Fulano Beltrano", "julgamento": "2025-05-05", "trecho": "x",
            "verificacao": "inteiro teor lido", "verificado_em": "2026-09-14"}
    r = run([P("(TJRS, AC 5001234-56.2024.8.21.0001, 3ª Câmara Cível, Rel. Des. Fulano Beltrano, j. 05/05/2025)")],
            precedentes=[f_rs])
    assert not r.erros, r.erros
    # 27. link do inteiro teor: ausente -> aviso; não oficial -> aviso; JURIS de outra peça -> erro
    j = "https://juris.tjro.jus.br/jurisprudencia/?id=%s&sistema_origem=PJESG&tipo=AC%%C3%%93RD%%C3%%83O"
    txt_ai = "(TJRO, AI 0819477-50.2024.8.22.0000, 2ª Câmara Cível, Rel. Des. Alexandre Miguel, j. 07/11/2025)"
    r = run([P(txt_ai)], precedentes=[f_ai])
    assert not r.erros and any("sem link do inteiro teor" in a for a in r.avisos), (r.erros, r.avisos)
    r = run([P(txt_ai)], precedentes=[dict(f_ai, link="https://www.jusbrasil.com.br/x")])
    assert not r.erros and any("fora de portal oficial" in a for a in r.avisos), (r.erros, r.avisos)
    r = run([P(txt_ai)], precedentes=[dict(f_ai, id_documento="30009487", link=j % "35915475")])
    assert any("abre outro documento" in e for e in r.erros), r.erros
    ok = dict(f_ai, id_documento="30009487", link=j % "30009487")
    r = run([P(txt_ai)], precedentes=[ok])
    assert not r.erros and not any("link" in a for a in r.avisos), (r.erros, r.avisos)
    # 28. carregar_links: só o link válido
    links = carregar_links({"precedentes": [ok, dict(F(), link="https://scon.stj.jus.br/SCON/x?y=1")]})
    assert set(links) == {("cnj", "08194775020248220000"), ("resp", "1959812")}, links
    assert carregar_links({"precedentes": [dict(ok, link=j % "1")]}) == {}
    assert segmentar_links("sem citação", links) == [("sem citação", None)]
    # 28b. segmentar_links: dentro de parênteses, o link cobre a REFERÊNCIA INTEIRA
    # (parênteses incluídos) — pedido do usuário, 14/09/2026 — não só o número.
    seg = segmentar_links("Como decidiu o TJRO (AI 0819477-50.2024.8.22.0000, Rel. X) e o STJ (REsp 1.959.812).", links)
    assert [u is not None for _, u in seg] == [False, True, False, True, False], seg
    assert seg[1] == ("(AI 0819477-50.2024.8.22.0000, Rel. X)", j % "30009487"), seg[1]
    assert seg[3] == ("(REsp 1.959.812)", links[("resp", "1959812")]), seg[3]
    assert "".join(t for t, _ in seg) == "Como decidiu o TJRO (AI 0819477-50.2024.8.22.0000, Rel. X) e o STJ (REsp 1.959.812)."
    # 28c. fora de parênteses, linka só o número (comportamento antigo, preservado)
    seg2 = segmentar_links("Vide AI 0819477-50.2024.8.22.0000, sem parênteses.", links)
    assert [u is not None for _, u in seg2] == [False, True, False], seg2
    assert seg2[1] == ("0819477-50.2024.8.22.0000", j % "30009487"), seg2[1]
    # 28d. duas citações COM link no MESMO parêntese: não expande (ambíguo) — cada
    # uma linka só o próprio número.
    dois_links = dict(links)
    dois_links[("resp", "1959812")] = links[("resp", "1959812")]
    seg3 = segmentar_links("(AI 0819477-50.2024.8.22.0000; REsp 1.959.812, ambos no mesmo sentido)", dois_links)
    urls3 = [u for t, u in seg3 if u]
    assert len(urls3) == 2 and set(urls3) == {j % "30009487", links[("resp", "1959812")]}, seg3
    assert not any(t.startswith("(") and t.endswith(")") for t, u in seg3 if u), seg3  # nenhum trecho é o grupo inteiro
    # 28e. atribuição de bloco `citacao` (só o parêntese, sem mais nada ao redor):
    # o parêntese INTEIRO vira o link.
    atrib = "(TJRO, Agravo de Instrumento 0819477-50.2024.8.22.0000, 2ª Câmara Cível, Rel. Des. Alexandre Miguel, j. 07/11/2025)"
    seg4 = segmentar_links(atrib, links)
    assert seg4 == [(atrib, j % "30009487")], seg4
    # 29. `url` (nome antigo, 49 notas do acervo e 35 fichas do vault) é lido como `link`
    velha = {k: v for k, v in ok.items() if k != "link"}
    velha["url"] = j % "30009487"
    assert carregar_links({"precedentes": [velha]}) == {("cnj", "08194775020248220000"): j % "30009487"}
    # 30. id_documento de ficha antiga: CNJ não é id de peça (não compara); lista de ids vale se tiver o do link
    assert problema_do_link(dict(ok, id_documento="0819477-50.2024.8.22.0000", link=j % "35915475")) is None
    assert problema_do_link(dict(ok, id_documento="30009487 (acórdão); 30009490 (ementa)", link=j % "30009490")) is None
    assert problema_do_link(dict(ok, id_documento="30009487 (acórdão); 30009490 (ementa)", link=j % "35915475"))[0] == "erro"
    # 31. domínio: TCU/TCE em .gov.br é oficial; API do JusRatio não é
    assert link_oficial("https://pesquisa.apps.tcu.gov.br/documento/acordao-completo/x")
    assert link_oficial("https://etce.tce.pe.gov.br/x") and link_oficial("https://tcero.tc.br/x")
    assert not link_oficial("https://api.jusratio.com.br/documento/x")
    assert not link_oficial("https://jusbrasil.com.br.exemplo.com/x") and not link_oficial("ftp://stj.jus.br/x")
    # 32. host do tribunal (14/09/2026, pedido do usuário — mesmo mecanismo agora no
    # TCE-RO): link do JURIS/TJRO numa ficha "tribunal": "TCE-RO" é erro mesmo sendo
    # domínio oficial (o `link_oficial` sozinho não pegaria — os dois são oficiais);
    # link do TCE-RO numa ficha "tribunal": "TJRO" também. Sem `tribunal` na ficha
    # (fichas antigas, como `f_ai`/`ok` acima), o check não se aplica — só entra quando
    # a ficha já diz de qual tribunal é.
    f_tcero = {"chave": "APL-TC 00055/26", "tribunal": "TCE-RO", "orgao": "Pleno",
               "relator": "José Euler Potyguara Pereira de Mello", "julgamento": "2026-06-22",
               "trecho": "descumprimento de determinação", "verificacao": "inteiro teor lido em parte (PDF)",
               "verificado_em": "2026-09-14"}
    lk_tcero = "https://tcero.tc.br/AbrirPdfConvidado/905cc845367c1a813573ebb5595598ce"
    assert host_errado_para_tribunal(f_tcero, lk_tcero) is None
    assert host_errado_para_tribunal(f_tcero, "https://tce.ro.gov.br/AbrirPdfConvidado/x") is None  # host antigo
    prob_tj_em_tcero = problema_do_link(dict(f_tcero, link=j % "30009487"))
    assert prob_tj_em_tcero and prob_tj_em_tcero[0] == "erro" and "outro tribunal" in prob_tj_em_tcero[1], prob_tj_em_tcero
    f_tjro_explicito = dict(ok, tribunal="TJRO")
    prob_tcero_em_tj = problema_do_link(dict(f_tjro_explicito, link=lk_tcero))
    assert prob_tcero_em_tj and prob_tcero_em_tj[0] == "erro" and "outro tribunal" in prob_tcero_em_tj[1], prob_tcero_em_tj
    assert problema_do_link(dict(f_tcero, link=lk_tcero)) is None
    txt_tcero = "Como decidiu o TCE-RO (APL-TC 00055/26, Pleno, Rel. José Euler Potyguara Pereira de Mello, j. 22/06/2026)."
    r = run([P(txt_tcero)], precedentes=[dict(f_tcero, link=lk_tcero)])
    assert not r.erros and not any("link" in a for a in r.avisos), (r.erros, r.avisos)
    seg_tcero = segmentar_links(txt_tcero, carregar_links({"precedentes": [dict(f_tcero, link=lk_tcero)]}))
    assert any(u == lk_tcero and t.startswith("(") and t.endswith(")") for t, u in seg_tcero), seg_tcero
    print("lint_citacoes: selftest OK (37 casos)")


def main():
    if len(sys.argv) == 2 and sys.argv[1] == "--selftest":
        _selftest()
        return
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    caminho = sys.argv[1]
    cfg = json.load(open(caminho, encoding="utf-8"))
    rel = lint(cfg, base_dir=os.path.dirname(os.path.abspath(caminho)))
    print(rel.texto())
    sys.exit(2 if rel.erros else 0)


if __name__ == "__main__":
    main()

