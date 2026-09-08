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
import datetime as dt
import os
import sys

MESES_REVERIFICACAO = 6
DIAS_PARA_PODA = 30
PASTAS = ("raw", "precedentes", "teses", "casos")


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


def _valor(bruto):
    bruto = bruto.strip()
    if bruto.startswith("["):
        fim = bruto.find("]")
        miolo = bruto[1:fim] if fim != -1 else bruto[1:]
        return [_desaspas(x) for x in miolo.split(",") if x.strip()]
    return _desaspas(_corta_comentario(bruto))


def le_frontmatter(caminho):
    """Devolve (dados, erro). erro != None quando a nota não é legível."""
    try:
        with open(caminho, encoding="utf-8") as fh:
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
    for linha in linhas[1:fim]:
        if not linha.strip() or linha.lstrip().startswith("#"):
            continue
        if ":" not in linha:
            continue
        chave, _, bruto = linha.partition(":")
        dados[chave.strip()] = _valor(bruto)
    return dados, None


def como_data(valor):
    try:
        return dt.date.fromisoformat(str(valor).strip())
    except (ValueError, AttributeError):
        return None


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
                dados, erro = le_frontmatter(caminho)
                notas.append(Nota(caminho, pasta, dados, erro))
    return notas


# --------------------------------------------------------------------- regras

def confere(base, hoje):
    achados = []      # (severidade, rotulo, caminho, mensagem)
    def anota(sev, rotulo, nota_ou_caminho, msg):
        alvo = getattr(nota_ou_caminho, "caminho", nota_ou_caminho)
        achados.append((sev, rotulo, os.path.relpath(alvo, base), msg))

    notas = coleta(base)
    if not notas:
        return achados, 0

    # notas ilegíveis saem da análise, mas são reportadas
    legiveis = []
    for nota in notas:
        if nota.erro:
            anota("erro", "MALFORMADO", nota, nota.erro)
        else:
            legiveis.append(nota)

    precedentes = {n.slug: n for n in legiveis if n.pasta == "precedentes"}
    teses = {n.slug: n for n in legiveis if n.pasta == "teses"}
    casos = [n for n in legiveis if n.pasta == "casos"]

    # 1. precedente com verificado_em vencido
    corte = hoje - dt.timedelta(days=MESES_REVERIFICACAO * 30)
    for slug, nota in sorted(precedentes.items()):
        bruto = nota.dados.get("verificado_em")
        data = como_data(bruto)
        if data is None:
            anota("erro", "MALFORMADO", nota,
                  "precedente sem verificado_em legível — não pode ser citado em peça")
        elif data < corte:
            anota("pendencia", "RECONFIRMAR", nota,
                  f"verificado_em {data.isoformat()}, há {(hoje - data).days} dias — "
                  "súmula cancelada e tema superado não avisam ninguém")

    # 2. tese sustentada por precedente superado
    for slug, nota in sorted(teses.items()):
        superados = [p for p in nota.lista("precedentes_favoraveis")
                     if p in precedentes and precedentes[p].dados.get("status") == "superado"]
        if superados:
            anota("pendencia", "REBAIXAR", nota,
                  "apoia-se em precedente superado (" + ", ".join(sorted(superados)) +
                  ") — rebaixar autoridade_da_base e revisar a tese")

    # 2b. referências que não resolvem
    for slug, nota in sorted(teses.items()):
        for alvo in nota.lista("precedentes_favoraveis"):
            if alvo not in precedentes:
                anota("erro", "REF-QUEBRADA", nota,
                      f"precedentes_favoraveis aponta para '{alvo}', que não existe em precedentes/")
    for nota in sorted(casos, key=lambda n: n.caminho):
        for alvo in nota.lista("tese_usada"):
            if alvo not in teses:
                anota("erro", "REF-QUEBRADA", nota,
                      f"tese_usada aponta para '{alvo}', que não existe em teses/")

    # 3. nota fora do índice
    caminho_indice = os.path.join(base, "indice.md")
    try:
        with open(caminho_indice, encoding="utf-8") as fh:
            indice = fh.read()
    except OSError:
        indice = None
        if legiveis:
            anota("pendencia", "FORA-DO-INDICE", caminho_indice,
                  "indice.md não existe, mas há notas guardadas — o índice é o que evita reler tudo")
    if indice is not None:
        for nota in sorted(notas, key=lambda n: n.caminho):
            if nota.slug not in indice:
                anota("pendencia", "FORA-DO-INDICE", nota,
                      "sem linha correspondente em indice.md — acrescentar ou decidir remover a nota")

    # 4. teste dos 30 dias, com referência transitiva
    teses_em_uso = set()
    for nota in casos:
        teses_em_uso.update(nota.lista("tese_usada"))

    for slug, nota in sorted(teses.items()):
        if slug in teses_em_uso:
            continue
        idade = nota.data_de_entrada
        if idade is None:
            anota("pendencia", "ARQUIVAR?", nota,
                  "nenhum caso em casos/ a usa, e a nota não tem data para medir a idade")
        elif (hoje - idade).days > DIAS_PARA_PODA:
            anota("pendencia", "ARQUIVAR?", nota,
                  f"nenhum caso em casos/ a usa, e está guardada há {(hoje - idade).days} dias")

    for slug, nota in sorted(precedentes.items()):
        # transitivo: basta que UMA tese sustentada por ele esteja em uso
        sustenta = [t for t, n in teses.items() if slug in n.lista("precedentes_favoraveis")]
        if any(t in teses_em_uso for t in sustenta):
            continue
        idade = nota.data_de_entrada
        if idade is not None and (hoje - idade).days <= DIAS_PARA_PODA:
            continue
        motivo = ("nenhuma tese o referencia" if not sustenta
                  else "as teses que ele sustenta (" + ", ".join(sorted(sustenta)) +
                       ") nunca foram usadas em nenhum caso")
        anota("pendencia", "ARQUIVAR?", nota, motivo)

    # 5. autoridade_da_base: solida exige 2+ precedentes
    for slug, nota in sorted(teses.items()):
        if nota.dados.get("autoridade_da_base") != "solida":
            continue
        quantos = len(nota.lista("precedentes_favoraveis"))
        if quantos < 2:
            anota("pendencia", "BASE-FRACA", nota,
                  f"autoridade_da_base: solida com {quantos} precedente(s) listado(s) — "
                  "solida exige dois julgamentos independentes")

    # 6. marcadores PENDENTE deixados no corpo
    for nota in sorted(legiveis, key=lambda n: n.caminho):
        try:
            with open(nota.caminho, encoding="utf-8") as fh:
                if "PENDENTE" in fh.read():
                    anota("pendencia", "PENDENTE", nota,
                          "tem marcador PENDENTE — campo não conferido, não citar em peça assim")
        except OSError:
            pass

    return achados, len(notas)


# --------------------------------------------------------------------- saída

ORDEM = {"erro": 0, "pendencia": 1}
CABECALHOS = {"erro": "ERROS ESTRUTURAIS", "pendencia": "PENDÊNCIAS"}


def relatorio(achados, total, base):
    print(f"Segundo cérebro: {base}")
    print(f"{total} nota(s) conferida(s) em {dt.date.today().isoformat()}\n")

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
    return relatorio(achados, total, base)


if __name__ == "__main__":
    sys.exit(main())
