#!/usr/bin/env python3
"""Confere a regra da página 1 em peça com resumo + caixa de destaque.

Regra do usuário (10/09/2026): a página 1 termina com a caixa de destaque;
o primeiro tópico (ex.: "I. Dos fatos") começa no topo da página 2.

Uso:
    python3 check_pagina1.py Peca.pdf [--caixa "RAZÕES PARA"] [--secao "I."]

Saída: OK (código 0) ou FALHA com a correção a fazer (código 1).
Correções possíveis:
  - primeiro tópico na página 1  -> acrescente 1 bloco {"tipo": "espaco"}
    ANTES do título "Resumo" e gere de novo;
  - caixa fora da página 1       -> retire 1 "espaco" antes do "Resumo"
    (ou, sem espaço a retirar, corte uma frase do resumo) e gere de novo.
Nunca use "quebra_pagina" logo depois da caixa: gera página em branco.
"""
import re
import sys
import unicodedata

try:
    import fitz  # PyMuPDF
except ImportError:
    sys.exit("PyMuPDF (fitz) não instalado: pip install pymupdf")


def norm(txt):
    """Junta hifenização de fim de linha e normaliza espaços/acentos."""
    txt = re.sub(r"-\s*\n\s*", "", txt)
    txt = re.sub(r"\s+", " ", txt)
    txt = unicodedata.normalize("NFKD", txt)
    return "".join(c for c in txt if not unicodedata.combining(c)).upper()


def linhas_corpo(page):
    """Linhas de texto da página, sem cabeçalho (logo/numeração) e rodapé."""
    h = page.rect.height
    saida = []
    for b in page.get_text("blocks"):
        x0, y0, x1, y1, texto = b[:5]
        if y0 < 0.10 * h or y1 > 0.92 * h:
            continue
        for ln in texto.splitlines():
            if ln.strip():
                saida.append((y0, ln.strip()))
    return sorted(saida)


def main():
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)
    pdf = args[0]
    caixa = "RAZÕES PARA"
    secao = "I."
    if "--caixa" in args:
        caixa = args[args.index("--caixa") + 1]
    if "--secao" in args:
        secao = args[args.index("--secao") + 1]

    doc = fitz.open(pdf)
    if len(doc) < 2:
        print("FALHA: a peça tem uma página só; a regra não se aplica.")
        return 1
    p1, p2 = doc[0], doc[1]
    t1 = norm(p1.get_text())
    ok = True

    if norm(caixa) not in t1:
        print('FALHA: o título da caixa ("%s") não está na página 1. '
              'Retire um "espaco" antes do título "Resumo" (ou corte uma '
              'frase do resumo) e gere de novo.' % caixa)
        ok = False

    padrao = re.compile(r"^" + re.escape(secao) + r"\s+\S")
    na_p1 = [ln for _, ln in linhas_corpo(p1) if padrao.match(ln)]
    if na_p1:
        print('FALHA: o primeiro tópico ("%s") está na página 1. '
              'Acrescente um {"tipo": "espaco"} antes do título "Resumo" '
              'e gere de novo.' % na_p1[0])
        ok = False

    corpo2 = linhas_corpo(p2)
    if not corpo2 or not padrao.match(corpo2[0][1]):
        primeira = corpo2[0][1] if corpo2 else "(vazia)"
        print('FALHA: a página 2 não começa pelo primeiro tópico; começa por '
              '"%s".' % primeira[:70])
        ok = False

    if ok:
        print('OK: caixa na página 1 e "%s" abrindo a página 2.' % corpo2[0][1])
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
