#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gate mecânico: recusa gerar o DOCX se o mapa do caso (mapa-de-caso) tem
pendência aberta ("## 7. Lacunas e ações" — seções "🔴 Antes de protocolar"
e "⏰ Prazo e preclusão") que o advogado ainda não confirmou.

Por que existe: a SKILL.md já dizia, em prosa, "PARE antes de gerar se o
mapa deixou qualquer coisa para resolver" — e mesmo assim, num ensaio de
15/09/2026, uma contestação saiu timbrada, assinada e pronta (com
"[A PREENCHER]" no lugar de CNPJ/endereço/nº do processo) sem que ninguém
tivesse sido perguntado item a item antes. Mesmo problema que motivou o
lint_citacoes.py: regra só em prosa se cumpre por fora quando ninguém a lê
no instante exato de montar o JSON. Isto é essa checagem em código.

Uso: python3 gate_mapa.py --selftest

Contrato (chamado de build_docx.py antes do lint de citações):
- Sem mapa referenciado (cfg["mapa_do_caso"]) nem `mapa*.md` na pasta do
  JSON de entrada OU na pasta do "output" (a peça costuma ir para a pasta
  do caso mesmo quando o JSON foi montado num scratchpad) -> sem gate.
  Cobre peça sem mapa: procuração, contrato, notificação, peça que não é
  contenciosa. "mapa_do_caso" explícito no JSON é a via recomendada — a
  busca automática é reserva, não o caminho principal.
- Mapa encontrado, mas "🔴 Antes de protocolar" e "⏰ Prazo e preclusão"
  sem item de lista (ou só o placeholder do template,
  "[lacuna] → [ação concreta]") -> sem gate, pendência resolvida.
- Mapa com pendência real e cfg sem "pendencias_mapa_confirmadas" (lista
  não vazia) -> ERRO: recusa gerar, lista as pendências encontradas.
- cfg com "pendencias_mapa_confirmadas" preenchido, mas nenhum bloco do
  documento contém a marca "[PENDENTE" -> ERRO: a SKILL.md exige que a
  pendência confirmada pelo advogado fique visível NO DOCUMENTO entregue,
  não só registrada na conversa.
- cfg com "pendencias_mapa_confirmadas" preenchido E algum bloco com
  "[PENDENTE" -> passa, com aviso listando o que foi confirmado.
"""
import glob
import json
import os
import re

_CANDIDATOS_GLOB = "mapa*.md"


def localizar_mapa(cfg, base_dir="."):
    caminho = cfg.get("mapa_do_caso")
    if caminho:
        if not os.path.isabs(caminho):
            caminho = os.path.join(base_dir, caminho)
        return caminho if os.path.isfile(caminho) else None

    # O JSON de entrada costuma ficar num scratchpad temporário, não na
    # pasta do caso — por isso a descoberta automática olha também a pasta
    # de saída ("output"), que é onde a peça de fato é salva. Ainda assim,
    # "mapa_do_caso" explícito no JSON é a via recomendada, não esta busca.
    pastas = [base_dir]
    saida = cfg.get("output")
    if saida:
        pasta_saida = os.path.dirname(os.path.abspath(saida)) or "."
        if pasta_saida not in pastas:
            pastas.append(pasta_saida)
    for pasta in pastas:
        preferido = os.path.join(pasta, "mapa-do-caso.md")
        if os.path.isfile(preferido):
            return preferido
        candidatos = sorted(glob.glob(os.path.join(pasta, _CANDIDATOS_GLOB)))
        if candidatos:
            return candidatos[0]
    return None


def _itens_da_secao(texto, emoji):
    """Bullets ('- ...') sob o primeiro '### <emoji> ...' até o próximo '##'."""
    m = re.search(r"^###\s*" + re.escape(emoji) + r".*$", texto, re.M)
    if not m:
        return []
    resto = texto[m.end():]
    prox = re.search(r"^##", resto, re.M)
    corpo = resto[:prox.start()] if prox else resto
    itens = []
    for linha in corpo.splitlines():
        linha = linha.strip()
        if linha.startswith("- "):
            itens.append(linha[2:].strip())
    # Placeholder do template não preenchido (mapa-de-caso/SKILL.md, Etapa 6):
    # "[lacuna] → [ação concreta]" — não é pendência real.
    return [i for i in itens
            if i and not (i.startswith("[") and i.endswith("]") and "→" in i)]


def pendencias_do_mapa(texto_mapa):
    return {"🔴": _itens_da_secao(texto_mapa, "🔴"),
            "⏰": _itens_da_secao(texto_mapa, "⏰")}


def checar(cfg, base_dir="."):
    """Retorna (erros: list[str], avisos: list[str])."""
    caminho = localizar_mapa(cfg, base_dir)
    if not caminho:
        return [], []
    try:
        texto_mapa = open(caminho, encoding="utf-8").read()
    except OSError as e:
        return [], ["mapa do caso (%s) não pôde ser lido: %s — gate de pendência não conferido"
                    % (caminho, e)]

    pend = pendencias_do_mapa(texto_mapa)
    todas = [("🔴", i) for i in pend["🔴"]] + [("⏰", i) for i in pend["⏰"]]
    if not todas:
        return [], []

    confirmadas = cfg.get("pendencias_mapa_confirmadas") or []
    if not confirmadas:
        erros = ["mapa do caso (%s) tem pendência sem decisão do advogado:" % caminho]
        erros += ["  [%s] %s" % par for par in todas]
        erros.append(
            "Liste cada uma para o advogado, item a item, e pergunte antes de montar o JSON "
            "(SKILL.md, \"Quando vem de um mapa de caso\"). Se ele mandar gerar assim mesmo, "
            "preencha \"pendencias_mapa_confirmadas\" com o que foi decidido e marque "
            "\"[PENDENTE: ...]\" no bloco afetado do documento.")
        return erros, []

    corpo = json.dumps(cfg.get("blocks") or [], ensure_ascii=False).lower()
    if "[pendente" not in corpo:
        return (["\"pendencias_mapa_confirmadas\" preenchido, mas nenhum bloco do documento traz "
                 "\"[PENDENTE\" — a pendência confirmada pelo advogado tem que ficar visível no "
                 "documento entregue, não só na conversa (SKILL.md, \"Quando vem de um mapa de "
                 "caso\")."], [])

    return [], ["mapa do caso: %d pendência(s) confirmada(s) pelo advogado: %s"
                % (len(confirmadas), "; ".join(confirmadas))]


# ------------------------------------------------------------------- selftest

def _selftest():
    import tempfile

    MAPA_SEM_PENDENCIA = """## 7. Lacunas e ações
### 🔴 Antes de protocolar
### 🟡 Atenção
### ⏰ Prazo e preclusão
### 🔍 Diligências fora dos autos
- [certidão, ata notarial, exibição, ofício] → [o que provaria]
"""

    MAPA_SO_TEMPLATE = """## 7. Lacunas e ações
### 🔴 Antes de protocolar
- [lacuna] → [ação concreta]
### 🟡 Atenção
### ⏰ Prazo e preclusão
"""

    MAPA_COM_PENDENCIA = """## 7. Lacunas e ações
### 🔴 Antes de protocolar (do lado do réu)
- Confirmar data de citação do réu para calcular o prazo de 15 dias úteis (art. 335 CPC).
- Confirmar com o cliente se de fato não houve a venda/o defeito alegado.
### 🟡 Atenção
### ⏰ Prazo e preclusão
- Prazo recursal vence em 20/09/2026, confirmar tempestividade antes de protocolar.
### 🔍 Diligências fora dos autos
"""

    def com_mapa(texto_mapa):
        d = tempfile.mkdtemp()
        open(os.path.join(d, "mapa-do-caso.md"), "w", encoding="utf-8").write(texto_mapa)
        return d

    # 1. Sem mapa nenhum na pasta -> sem gate.
    d = tempfile.mkdtemp()
    erros, avisos = checar({"blocks": []}, base_dir=d)
    assert not erros and not avisos, (erros, avisos)

    # 2. Mapa presente, seções vazias -> sem gate.
    d = com_mapa(MAPA_SEM_PENDENCIA)
    erros, avisos = checar({"blocks": []}, base_dir=d)
    assert not erros and not avisos, (erros, avisos)

    # 3. Mapa só com o placeholder do template (não preenchido) -> não conta.
    d = com_mapa(MAPA_SO_TEMPLATE)
    erros, avisos = checar({"blocks": []}, base_dir=d)
    assert not erros and not avisos, (erros, avisos)

    # 4. Pendência real, sem confirmação -> ERRO, lista os 3 itens (2x 🔴 + 1x ⏰).
    d = com_mapa(MAPA_COM_PENDENCIA)
    erros, avisos = checar({"blocks": []}, base_dir=d)
    assert erros and not avisos, (erros, avisos)
    assert sum(1 for e in erros if "Confirmar data de citação" in e) == 1, erros
    assert sum(1 for e in erros if "Confirmar com o cliente" in e) == 1, erros
    assert sum(1 for e in erros if "Prazo recursal vence" in e) == 1, erros

    # 5. Confirmado pelo advogado, mas sem "[PENDENTE" em nenhum bloco -> ERRO.
    cfg = {"blocks": [{"tipo": "paragrafo", "texto": "Sem marca de pendência aqui."}],
           "pendencias_mapa_confirmadas": ["gera assim mesmo, cliente confirmou por telefone"]}
    erros, avisos = checar(cfg, base_dir=d)
    assert erros and "[PENDENTE" in erros[0], erros

    # 6. Confirmado E com "[PENDENTE" em algum bloco -> passa, com aviso.
    cfg = {"blocks": [{"tipo": "paragrafo", "texto": "Réu foi citado. [PENDENTE: confirmar data exata]"}],
           "pendencias_mapa_confirmadas": ["gera assim mesmo, cliente confirmou por telefone"]}
    erros, avisos = checar(cfg, base_dir=d)
    assert not erros, erros
    assert avisos and "1 pendência" in avisos[0], avisos

    # 7. "mapa_do_caso" explícito, nome fora do padrão mapa*.md.
    d2 = tempfile.mkdtemp()
    open(os.path.join(d2, "diagnostico-caso-x.md"), "w", encoding="utf-8").write(MAPA_COM_PENDENCIA)
    erros, avisos = checar({"blocks": [], "mapa_do_caso": "diagnostico-caso-x.md"}, base_dir=d2)
    assert erros, erros

    # 8. JSON montado num scratchpad (sem mapa lá), peça salva na pasta do
    # caso (com mapa lá) -> a busca pela pasta de "output" tem de achar.
    scratchpad = tempfile.mkdtemp()
    pasta_caso = com_mapa(MAPA_COM_PENDENCIA)
    cfg = {"blocks": [], "output": os.path.join(pasta_caso, "Peca.docx")}
    erros, avisos = checar(cfg, base_dir=scratchpad)
    assert erros, erros

    print("gate_mapa: selftest OK (8 casos)")


if __name__ == "__main__":
    import sys
    if len(sys.argv) == 2 and sys.argv[1] == "--selftest":
        _selftest()
    else:
        sys.exit("Uso: python3 gate_mapa.py --selftest")
