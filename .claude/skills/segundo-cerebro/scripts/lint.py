#!/usr/bin/env python3
"""
Lint do segundo cérebro — confere a base de conhecimento em ~/segundo-cerebro/.

Não julga nada. Cada regra aqui tem exatamente uma resposta certa, calculável a
partir do frontmatter das notas: por isso é código, e não instrução para um
modelo seguir. O que exige julgamento (a tese se sustenta? o precedente é
aplicável?) continua fora daqui, com o advogado.

Roda só quando chamado. Lê arquivos locais e escreve na saída padrão — nenhuma
rede, nenhuma dependência externa, nada sai da máquina. As notas podem conter
trecho colado de autos; tratar como o arquivo mais sensível da pasta.

Uso:
    python3 lint.py                 # confere ~/segundo-cerebro/
    python3 lint.py --base CAMINHO  # confere outra pasta (testes)
    python3 lint.py --hoje AAAA-MM-DD

Saída:
    0  nada a fazer
    1  há pendências para o advogado resolver
    2  há erro estrutural (nota ilegível ou referência quebrada)
"""

import argparse
import calendar
import datetime as dt
import os
import re
import sys

MESES_REVERIFICACAO = 6
DIAS_PARA_PODA = 30

# raw/ guarda fonte bruta — acórdão colado, trecho de doutrina. A spec não lhe
# dá frontmatter, então ela entra só na conferência de índice.
PASTAS_COM_FRONTMATTER = ("precedentes", "teses", "casos")
PASTAS = PASTAS_COM_FRONTMATTER + ("raw",)

TIPO_DA_PASTA = {"precedentes": "precedente", "teses": "tese", "casos": "caso"}

# Súmula é cancelada, tema é superado, acórdão é revogado. Todas dizem a mesma
# coisa para efeito de citar em peça: não cite.
STATUS_MORTO = {"superado", "superada", "cancelado", "cancelada",
                "revogado", "revogada", "sem eficacia", "sem eficácia"}
STATUS_VIVO = {"vigente", "vigentes", "ativo", "ativa", "valido", "válido"}

# O marcador que a spec define é "PENDENTE: ...", com dois-pontos. Exigir os
# dois-pontos e a fronteira de palavra é o que impede casar dentro de
# INDEPENDENTEMENTE — redação do art. 14 do CDC, e em caixa alta em toda
# ementa de responsabilidade objetiva.
RE_PENDENTE = re.compile(r"\bPENDENTE\s*:")


def classifica_status(bruto):
    """morto · vivo · desconhecido. Casa por palavra, não por igualdade: quem
    escreve 'superado (Tema 69)' quer dizer superado. Negação ('não superado')
    devolve desconhecido — na dúvida quem decide é o advogado, não o lint."""
    s = str(bruto or "").strip().lower()
    if not s:
        return "ausente"
    negado = re.search(r"\bn[ãa]o\b", s) is not None
    palavra = lambda termos: any(
        re.search(r"\b" + re.escape(x) + r"\b", s) for x in termos)
    if negado:
        return "desconhecido"
    if palavra(STATUS_MORTO):
        return "morto"
    if palavra(STATUS_VIVO):
        return "vivo"
    return "desconhecido"


# ---------------------------------------------------------------- frontmatter

def _corta_comentario(valor):
    """Remove comentário ' # ...' fora de aspas. '#' colado (url#frag) fica."""
    if valor[:1] in ('"', "'"):
        aspas = valor[0]
        fim = valor.find(aspas, 1)
        return valor[1:fim] if fim != -1 else valor[1:]
    for i, ch in enumerate(valor):
        if ch == "#" and i > 0 and valor[i - 1] in " \t":
            return valor[:i].rstrip()
    return valor.rstrip()


def _desaspas(item):
    item = item.strip()
    if len(item) >= 2 and item[0] == item[-1] and item[0] in ('"', "'"):
        return item[1:-1]
    return item


def _lista_inline(bruto):
    """['a', 'b'] a partir de '[a, b]'. Erro se o ] não fecha na linha."""
    fim = bruto.find("]")
    if fim == -1:
        raise ValueError("lista aberta com [ e não fechada na mesma linha")
    return [_desaspas(x) for x in bruto[1:fim].split(",") if x.strip()]


def _escalar(bruto):
    return _desaspas(_corta_comentario(bruto.strip()))


def le_frontmatter(caminho):
    """Devolve (dados, erro). erro != None quando a nota não é legível."""
    try:
        with open(caminho, encoding="utf-8-sig") as fh:   # -sig come o BOM
            linhas = fh.read().splitlines()
    except (OSError, UnicodeDecodeError) as exc:
        return {}, f"não deu para ler: {exc}"

    if not linhas or not any(l.strip() for l in linhas):
        return {}, "arquivo vazio"
    if linhas[0].strip() != "---":
        return {}, "sem frontmatter (não começa com ---)"

    fim = None
    for i in range(1, len(linhas)):
        if linhas[i].strip() == "---":
            fim = i
            break
    if fim is None:
        return {}, "frontmatter aberto e nunca fechado"

    dados = {}
    chave_aberta = None          # lista em bloco: "chave:" e depois "  - item"
    for linha in linhas[1:fim]:
        nua = linha.strip()
        if not nua or nua.startswith("#"):
            continue

        if nua.startswith("- ") or nua == "-":
            if chave_aberta is None:
                continue
            item = _escalar(nua[1:])
            if item:
                dados[chave_aberta].append(item)
            continue

        if ":" not in linha:
            continue
        chave, _, bruto = linha.partition(":")
        chave = chave.strip()
        bruto = bruto.strip()
        chave_aberta = None

        if not bruto:
            # ou é lista em bloco (itens vêm abaixo), ou campo vazio de verdade
            dados[chave] = []
            chave_aberta = chave
        elif bruto.startswith("["):
            try:
                dados[chave] = _lista_inline(bruto)
            except ValueError as exc:
                return {}, f"campo '{chave}': {exc}"
        else:
            dados[chave] = _escalar(bruto)

    return dados, None


def como_data(valor):
    try:
        return dt.date.fromisoformat(str(valor).strip())
    except (ValueError, AttributeError, TypeError):
        return None


def menos_meses(data, meses):
    ano, mes = data.year, data.month - meses
    while mes <= 0:
        mes += 12
        ano -= 1
    return dt.date(ano, mes, min(data.day, calendar.monthrange(ano, mes)[1]))


# --------------------------------------------------------------------- coleta

class Nota:
    def __init__(self, caminho, pasta, dados, erro):
        self.caminho = caminho
        self.pasta = pasta
        self.slug = os.path.splitext(os.path.basename(caminho))[0]
        self.dados = dados
        self.erro = erro

    def lista(self, chave):
        valor = self.dados.get(chave, [])
        if isinstance(valor, list):
            return valor
        return [valor] if valor else []

    def texto(self):
        try:
            with open(self.caminho, encoding="utf-8-sig") as fh:
                return fh.read()
        except (OSError, UnicodeDecodeError):
            return ""

    @property
    def data_de_entrada(self):
        for chave in ("verificado_em", "ultima_revisao", "data", "julgamento"):
            data = como_data(self.dados.get(chave))
            if data:
                return data
        return None


def coleta(base):
    notas = []
    for pasta in PASTAS:
        raiz = os.path.join(base, pasta)
        if not os.path.isdir(raiz):
            continue
        for atual, _, arquivos in os.walk(raiz):
            for nome in sorted(arquivos):
                if not nome.endswith(".md"):
                    continue
                caminho = os.path.join(atual, nome)
                if pasta in PASTAS_COM_FRONTMATTER:
                    dados, erro = le_frontmatter(caminho)
                else:
                    dados, erro = {}, None      # raw/ é fonte bruta, sem schema
                notas.append(Nota(caminho, pasta, dados, erro))
    return notas


# --------------------------------------------------------------------- regras

def confere(base, hoje):
    achados = []

    def anota(sev, rotulo, alvo, msg):
        caminho = getattr(alvo, "caminho", alvo)
        achados.append((sev, rotulo, os.path.relpath(caminho, base), msg))

    notas = coleta(base)
    if not notas:
        return achados, 0

    ilegiveis, legiveis = [], []
    for nota in notas:
        if nota.erro:
            anota("erro", "MALFORMADO", nota, nota.erro)
            ilegiveis.append(nota)
        else:
            legiveis.append(nota)

    # As listas guardam TODAS as notas legíveis; os dicts só resolvem
    # referência por slug. Separar os dois é o que impede que duas notas de
    # mesmo nome em subpastas diferentes façam uma sumir das regras.
    l_precedentes = [n for n in legiveis if n.pasta == "precedentes"]
    l_teses = [n for n in legiveis if n.pasta == "teses"]
    l_casos = [n for n in legiveis if n.pasta == "casos"]

    def indexa(lista):
        por_slug = {}
        for nota in sorted(lista, key=lambda n: n.caminho):
            if nota.slug in por_slug:
                anota("erro", "MALFORMADO", nota,
                      f"slug '{nota.slug}' repetido — já existe em "
                      f"{os.path.relpath(por_slug[nota.slug].caminho, base)}; "
                      "referências por slug ficam ambíguas")
            else:
                por_slug[nota.slug] = nota
        return por_slug

    precedentes = indexa(l_precedentes)
    teses = indexa(l_teses)

    # slugs que existem no disco mas não puderam ser lidos: uma referência a
    # eles não é "quebrada", é consequência do MALFORMADO já reportado
    slugs_ilegiveis = {n.slug for n in ilegiveis}

    # tipo: declarado x pasta onde está
    for nota in sorted(legiveis, key=lambda n: n.caminho):
        esperado = TIPO_DA_PASTA.get(nota.pasta)
        declarado = nota.dados.get("tipo")
        if esperado and declarado and declarado != esperado:
            anota("erro", "MALFORMADO", nota,
                  f"declara 'tipo: {declarado}' mas está em {nota.pasta}/ — "
                  f"as regras de {esperado} não se aplicam a ela onde está")

    # 1. precedente com verificado_em vencido, ausente ou impossível
    corte = menos_meses(hoje, MESES_REVERIFICACAO)
    for nota in sorted(l_precedentes, key=lambda n: n.caminho):
        data = como_data(nota.dados.get("verificado_em"))
        if data is None:
            anota("erro", "MALFORMADO", nota,
                  "precedente sem verificado_em legível (use AAAA-MM-DD) — "
                  "sem data conferida não pode ser citado em peça")
        elif data > hoje:
            anota("erro", "MALFORMADO", nota,
                  f"verificado_em {data.isoformat()} está no futuro — data "
                  "impossível isenta a nota de reconfirmação para sempre")
        elif data < corte:
            anota("pendencia", "RECONFIRMAR", nota,
                  f"verificado_em {data.isoformat()}, há {(hoje - data).days} dias — "
                  "súmula cancelada e tema superado não avisam ninguém")

    # status fora do vocabulário: não dá para saber se vale ou não vale
    for nota in sorted(l_precedentes, key=lambda n: n.caminho):
        bruto = nota.dados.get("status")
        if classifica_status(bruto) == "desconhecido":
            anota("pendencia", "STATUS?", nota,
                  f"status: {bruto} — não está entre vigente e "
                  "superado/cancelado/revogado, então o lint não sabe se a "
                  "tese que se apoia nele deve ser rebaixada")

    def morto(slug):
        nota = precedentes.get(slug)
        if not nota:
            return False
        return classifica_status(nota.dados.get("status")) == "morto"

    # 2. tese sustentada por precedente que já morreu
    for nota in sorted(l_teses, key=lambda n: n.caminho):
        mortos = sorted({p for p in nota.lista("precedentes_favoraveis") if morto(p)})
        if mortos:
            anota("pendencia", "REBAIXAR", nota,
                  "apoia-se em precedente sem vigência (" + ", ".join(mortos) +
                  ") — rebaixar autoridade_da_base e revisar a tese")

    # 2b. referências que não resolvem
    for nota in sorted(l_teses, key=lambda n: n.caminho):
        for alvo in nota.lista("precedentes_favoraveis"):
            if alvo not in precedentes and alvo not in slugs_ilegiveis:
                anota("erro", "REF-QUEBRADA", nota,
                      f"precedentes_favoraveis aponta para '{alvo}', "
                      "que não existe em precedentes/")
    for nota in sorted(l_casos, key=lambda n: n.caminho):
        for alvo in nota.lista("tese_usada"):
            if alvo not in teses and alvo not in slugs_ilegiveis:
                anota("erro", "REF-QUEBRADA", nota,
                      f"tese_usada aponta para '{alvo}', que não existe em teses/")

    # 3. nota fora do índice — linha a linha, com fronteira: slugs jurídicos
    #    são prefixais (stj-resp-N é prefixo de stj-resp-N-tema), então casar
    #    por substring no arquivo inteiro deixa passar a nota não indexada
    caminho_indice = os.path.join(base, "indice.md")
    indexados = None
    try:
        with open(caminho_indice, encoding="utf-8-sig") as fh:
            indexados = set()
            for linha in fh:
                indexados.update(re.findall(r"[A-Za-z0-9][A-Za-z0-9._-]*", linha))
    except OSError:
        if legiveis:
            anota("pendencia", "FORA-DO-INDICE", caminho_indice,
                  "indice.md não existe, mas há notas guardadas — "
                  "o índice é o que evita reler tudo")
    except UnicodeDecodeError as exc:
        anota("erro", "MALFORMADO", caminho_indice,
              f"indice.md não está em UTF-8 ({exc}) — nenhuma nota pôde ser "
              "conferida contra o índice")

    if indexados is not None:
        for nota in sorted(notas, key=lambda n: n.caminho):
            if nota.slug not in indexados:
                anota("pendencia", "FORA-DO-INDICE", nota,
                      "sem linha correspondente em indice.md — "
                      "acrescentar ou decidir remover a nota")

    # 4. teste dos 30 dias, com referência transitiva nos dois sentidos
    teses_em_uso = set()
    for nota in l_casos:
        teses_em_uso.update(nota.lista("tese_usada"))

    for nota in sorted(l_teses, key=lambda n: n.caminho):
        if nota.slug in teses_em_uso:
            continue
        idade = nota.data_de_entrada
        if idade is None:
            anota("pendencia", "ARQUIVAR?", nota,
                  "nenhum caso em casos/ a usa, e a nota não tem data para "
                  "medir a idade")
        elif (hoje - idade).days > DIAS_PARA_PODA:
            anota("pendencia", "ARQUIVAR?", nota,
                  f"nenhum caso em casos/ a usa, e está guardada há "
                  f"{(hoje - idade).days} dias")

    for nota in sorted(l_precedentes, key=lambda n: n.caminho):
        # O elo pode estar escrito de qualquer um dos dois lados, e o
        # precedente contrário só aparece em contra_teses. Ler um sentido só
        # acusa de órfão todo precedente da parte adversa, para sempre.
        ligadas = set(nota.lista("teses"))
        for tese in l_teses:
            if nota.slug in tese.lista("precedentes_favoraveis") or \
               nota.slug in tese.lista("contra_teses"):
                ligadas.add(tese.slug)
        if any(t in teses_em_uso for t in ligadas):
            continue
        idade = nota.data_de_entrada
        if idade is not None and (hoje - idade).days <= DIAS_PARA_PODA:
            continue
        motivo = ("nenhuma tese o referencia, e ele não declara nenhuma no campo teses:"
                  if not ligadas else
                  "as teses ligadas a ele (" + ", ".join(sorted(ligadas)) +
                  ") nunca foram usadas em nenhum caso")
        anota("pendencia", "ARQUIVAR?", nota, motivo)

    # 5. autoridade_da_base: solida exige 2+ precedentes
    for nota in sorted(l_teses, key=lambda n: n.caminho):
        if str(nota.dados.get("autoridade_da_base", "")).strip().lower() != "solida":
            continue
        quantos = len(nota.lista("precedentes_favoraveis"))
        if quantos < 2:
            anota("pendencia", "BASE-FRACA", nota,
                  f"autoridade_da_base: solida com {quantos} precedente(s) "
                  "listado(s) — solida exige dois julgamentos independentes")

    # 6. marcadores PENDENTE deixados na nota
    for nota in sorted(legiveis, key=lambda n: n.caminho):
        if RE_PENDENTE.search(nota.texto()):
            anota("pendencia", "PENDENTE", nota,
                  "tem marcador PENDENTE: — campo não conferido, "
                  "não citar em peça assim")

    return achados, len(notas)


# --------------------------------------------------------------------- saída

ORDEM = {"erro": 0, "pendencia": 1}
CABECALHOS = {"erro": "ERROS ESTRUTURAIS", "pendencia": "PENDÊNCIAS"}


def relatorio(achados, total, base, hoje):
    print(f"Segundo cérebro: {base}")
    print(f"{total} nota(s) conferida(s) em {hoje.isoformat()}\n")

    if not total:
        print("Nada guardado ainda — nada a conferir.")
        return 0
    if not achados:
        print("Nenhum achado. Base em dia.")
        return 0

    achados.sort(key=lambda a: (ORDEM[a[0]], a[1], a[2]))
    atual = None
    for sev, rotulo, caminho, msg in achados:
        if sev != atual:
            atual = sev
            print(f"\n== {CABECALHOS[sev]} ==\n")
        print(f"[{rotulo}] {caminho}")
        print(f"    {msg}")

    erros = sum(1 for a in achados if a[0] == "erro")
    print(f"\n{len(achados)} achado(s): {erros} erro(s), {len(achados) - erros} pendência(s).")
    print("\nO lint conta o que dá para contar. Se dois precedentes vêm do mesmo")
    print("julgamento, a base não é sólida — e só você sabe disso olhando as notas.")
    return 2 if erros else 1


def main():
    p = argparse.ArgumentParser(description="Confere a base do segundo cérebro.")
    p.add_argument("--base", default=os.path.expanduser("~/segundo-cerebro"))
    p.add_argument("--hoje", default=None, help="data de referência AAAA-MM-DD (testes)")
    args = p.parse_args()

    base = os.path.abspath(os.path.expanduser(args.base))
    if not os.path.isdir(base):
        print(f"Pasta não encontrada: {base}")
        print("Consulta em base inexistente é 'nada guardado ainda', não erro.")
        return 0

    hoje = como_data(args.hoje) if args.hoje else dt.date.today()
    if hoje is None:
        print(f"--hoje inválido: {args.hoje}", file=sys.stderr)
        return 2

    achados, total = confere(base, hoje)
    return relatorio(achados, total, base, hoje)


if __name__ == "__main__":
    sys.exit(main())
