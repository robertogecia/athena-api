#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gera DOCX de petição com o timbre e a formatação padrão do escritório
Roberto Grécia (Advocacia e Consultoria Jurídica).

Template e estilo extraídos de um agravo de instrumento real do escritório
"com tipografia": timbre na 1ª página, rodapé com contatos, numeração
de páginas, Segoe UI justificado, assinatura manuscrita — além dos elementos
de destaque que dão o acabamento "desenhado": caixa de destaque (quadro
azul-marinho + lista), títulos de seção e pedidos com marcador em negrito.

Uso:
    python3 build_docx.py entrada.json

Formato do JSON de entrada:
{
  "output": "/caminho/Peca.docx",
  "blocks": [
    {"tipo": "enderecamento", "texto": "AO EGRÉGIO TRIBUNAL ..."},
    {"tipo": "processo",      "texto": "Processo nº 0000000-00.0000.0.00.0000"},
    {"tipo": "espaco"},
    {"tipo": "paragrafo",     "texto": "**PARTE**, qualificação ... apresentar **PEÇA** ..."},
    {"tipo": "titulo",        "texto": "I. Resumo"},
    {"tipo": "paragrafo",     "texto": "Texto com *itálico*, **negrito**, __sublinhado__."},
    {"tipo": "caixa_destaque",
     "titulo": "RAZÕES PARA CONCESSÃO DA LIMINAR",
     "itens": ["Primeiro ponto.", "Segundo ponto.", "Terceiro ponto."]},
    {"tipo": "tabela", "titulo": "Quadro comparativo (legenda opcional)",
     "colunas": ["Produto", "Rendimento", "Risco"],
     "linhas": [["Fundo A", "10% a.a.", "Baixo"], ["Fundo B", "15% a.a.", "Alto"]]},
    {"tipo": "subtitulo",     "texto": "II.1. Do ..."},
    {"tipo": "citacao",       "texto": "Citação longa de ementa/doutrina/decisão, recuo 1cm, 10,5pt, entre aspas (automático), sem itálico; a atribuição fica fora das aspas.",
     "atribuicao": "(STJ, REsp 1.234.567/SP, Rel. Min. Fulano de Tal, j. 10/10/2020)"},
    {"tipo": "paragrafo",     "texto": "Dispõe o art. 1º do CPC:"},
    {"tipo": "citacao",       "texto": "O processo civil será ordenado, disciplinado e interpretado conforme os valores e as normas fundamentais estabelecidos na Constituição da República Federativa do Brasil, observando-se as disposições deste Código."},
    {"tipo": "titulo",        "texto": "V. Dos pedidos"},
    {"tipo": "paragrafo",     "texto": "Requer:"},
    {"tipo": "pedido", "marcador": "A.", "texto": "Primeiro pedido, com desdobramentos:"},
    {"tipo": "pedido", "marcador": "a.1)", "texto": "subitem do pedido A;", "nivel": 2},
    {"tipo": "pedido", "marcador": "B.", "texto": "Segundo pedido, subsidiário."},
    {"tipo": "fecho",
     "data": "2 de julho de 2026",
     "recurso": true,
     "nome": "Roberto Grécia Bessa",
     "oab": "OAB/RO 7865",
     "assinatura": true}
  ],
  "precedentes": [
    {"chave": "REsp 1.234.567/SP", "tribunal": "STJ", "orgao": "Terceira Turma",
     "relator": "Min. Fulano de Tal", "julgamento": "2020-10-10",
     "trecho": "Citação longa de ementa/doutrina/decisão, recuo 1cm, 10,5pt, entre aspas (automático), sem itálico; a atribuição fica fora das aspas.",
     "verificado_em": "2026-09-04", "verificacao": "inteiro teor lido"}
  ],
  "processos_do_caso": []
}

"precedentes" é a lista de fichas do pesquisador-juridico (uma por julgado
citado); sem ficha, ou com relator/data/órgão/aspas divergentes da ficha, o
script recusa gerar (lint_citacoes.py). "processos_do_caso" lista números
CNJ do próprio caso que a peça menciona como fato, não como precedente (o
número do bloco "processo" já entra sozinho). "permitir_nao_verificado":
true rebaixa erros a avisos — só em último caso, e dizendo isso ao usuário.

Antes disso, o script também recusa gerar se houver mapa-do-caso.md (ou
mapa*.md, na pasta do JSON ou do "output") com pendência aberta em
"🔴 Antes de protocolar" ou "⏰ Prazo e preclusão" (ver gate_mapa.py e
SKILL.md, "Quando vem de um mapa de caso"). Escape hatch: "pendencias_mapa_
confirmadas" (lista não vazia, o que o advogado decidiu) + pelo menos um
bloco com "[PENDENTE" no texto. "mapa_do_caso": "<caminho>" aponta o mapa
explicitamente quando ele não estiver onde o script procura sozinho.

A cidade do fecho é sempre "Porto Velho/RO" (sede do escritório, não a
comarca do processo) — passe só "data"; "cidade_data" é aceito como
escape hatch bruto apenas se pedirem outra cidade explicitamente.

O fecho NÃO tem encerramento padrão: "recurso": true/false é obrigatório
(ou "encerramento" com o texto exato para casos fora do padrão). Recurso
(agravo, apelação, recurso especial/extraordinário) -> "pede provimento".
Não-recurso (petição inicial, contestação, cumprimento de sentença,
embargos de declaração) -> "pede deferimento". Nunca adivinhar: sem um
dos dois, o script recusa gerar o documento.

Marcação inline: **negrito**, *itálico*, __sublinhado__.

Link do inteiro teor: todo número de julgado citado cuja ficha traga `link` de
portal oficial vira hiperlink (azul-marinho, sublinhado) para o inteiro teor, no
DOCX e no PDF — o juiz clica e confere a fonte. O texto da peça não muda; quem
decide se o link entra é o lint (lint_citacoes.problema_do_link).
"""
import json
import os
import re
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(HERE, "..", "assets", "template.docx")
SIG_DRAWING = os.path.join(HERE, "..", "assets", "sig_drawing.xml")
sys.path.insert(0, HERE)
from lint_citacoes import carregar_links, lint, segmentar_links  # noqa: E402
from gate_mapa import checar as checar_pendencias_mapa  # noqa: E402

FONT = '<w:rFonts w:ascii="Segoe UI" w:hAnsi="Segoe UI" w:cs="Segoe UI"/>'
NAVY = "1F497D"   # azul-marinho do timbre (themeColor text2)
GRAY = "F2F2F2"   # cinza-claro da caixa de destaque
REL_HYPERLINK = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink"

# ident da citação -> url do inteiro teor (preenchido no main, depois do lint)
_LINKS = {}
# url -> rId da relação de hiperlink criada no document.xml.rels
_RELS = {}
# urls já usadas como hiperlink em algum trecho anterior do documento — só a
# primeira menção de cada julgado/tema vira link (pedido do usuário,
# 15/09/2026: peça com "Tema 1300"/"Tema 1150" citados em toda frase saía com
# hiperlink em cada menção, poluindo o texto corrido).
_LINKED_URLS = set()
# citação de classe "tema" (bare "Tema 1300", "Tema 1150", sem número de
# processo/REsp junto) nunca vira link (pedido do usuário, 15/09/2026: um
# tema repetitivo citado solto no meio da frase não precisa apontar para o
# inteiro teor — reservar o link para a citação formal do julgado, quando
# ela tiver classe própria, ex. "REsp 1.895.936" ou o número do acórdão).
_CLASSES_SEM_LINK = {"tema"}


def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _run_link(texto, rpr, url):
    rid = _RELS.setdefault(url, "rIdLk%d" % (len(_RELS) + 1))
    # Sobre fundo colorido (texto já tem cor própria), só o sublinhado marca o link.
    extra = ('<w:u w:val="single"/>' if "<w:color" in rpr
             else '<w:color w:val="%s"/><w:u w:val="single"/>' % NAVY)
    return ('<w:hyperlink r:id="%s" w:history="1"><w:r>%s<w:t xml:space="preserve">%s</w:t></w:r></w:hyperlink>'
            % (rid, rpr.replace("</w:rPr>", extra + "</w:rPr>"), esc(texto)))


def runs(texto, base_rpr):
    """Converte **negrito** / *itálico* / __sublinhado__ em runs; número de
    julgado com link oficial na ficha vira hiperlink para o inteiro teor."""
    out = []
    tokens = re.split(r"(\*\*.+?\*\*|__.+?__|\*[^*]+?\*)", texto)
    for tok in tokens:
        if not tok:
            continue
        extra = ""
        if tok.startswith("**") and tok.endswith("**"):
            tok, extra = tok[2:-2], "<w:b/><w:bCs/>"
        elif tok.startswith("__") and tok.endswith("__"):
            tok, extra = tok[2:-2], '<w:u w:val="single"/>'
        elif tok.startswith("*") and tok.endswith("*") and len(tok) > 2:
            tok, extra = tok[1:-1], "<w:i/><w:iCs/>"
        rpr = base_rpr.replace("</w:rPr>", extra + "</w:rPr>")
        links_disponiveis = {k: v for k, v in _LINKS.items()
                              if v not in _LINKED_URLS and k[0] not in _CLASSES_SEM_LINK}
        for pedaco, url in segmentar_links(tok, links_disponiveis):
            if not pedaco:
                continue
            if url:
                out.append(_run_link(pedaco, rpr, url))
                _LINKED_URLS.add(url)
            else:
                out.append('<w:r>%s<w:t xml:space="preserve">%s</w:t></w:r>' % (rpr, esc(pedaco)))
    return "".join(out)


def para(ppr, conteudo):
    return "<w:p><w:pPr>%s</w:pPr>%s</w:p>" % (ppr, conteudo)


def bloco(b):
    t = b.get("tipo")
    texto = b.get("texto", "")

    if t == "enderecamento":
        # 12pt (sz 24) negrito — padrão dos endereçamentos a tribunal/juízo
        rpr = "<w:rPr>%s<w:b/><w:bCs/><w:sz w:val=\"24\"/><w:szCs w:val=\"24\"/></w:rPr>" % FONT
        ppr = '<w:spacing w:before="0" w:after="240"/><w:jc w:val="both"/>' + rpr
        return para(ppr, runs(texto, rpr))

    if t == "processo":
        rpr = "<w:rPr>%s<w:i/><w:iCs/><w:sz w:val=\"22\"/><w:szCs w:val=\"22\"/></w:rPr>" % FONT
        ppr = '<w:spacing w:before="0" w:after="240"/><w:jc w:val="both"/>' + rpr
        return para(ppr, runs(texto, rpr))

    if t == "titulo":
        rpr = "<w:rPr>%s<w:b/><w:bCs/><w:sz w:val=\"28\"/><w:szCs w:val=\"28\"/></w:rPr>" % FONT
        conteudo = runs(texto, rpr)
        if b.get("centralizado"):
            # Título principal centralizado -- usado em documentos para o
            # cliente (parecer, etc.) quando o título nomeia o documento
            # inteiro, não abre uma seção numerada. Incompatível com
            # "linha" (a régua é pensada para títulos de seção alinhados
            # à esquerda/justificados).
            ppr = '<w:keepNext/><w:spacing w:before="360" w:after="240"/><w:jc w:val="center"/>' + rpr
            return para(ppr, conteudo)
        if b.get("linha"):
            # régua horizontal após o título, no estilo do 1º título do
            # agravo de referência. Implementada como tab com leader
            # sólido (não como shape ancorada nem estilo "Título" nomeado
            # do Word) -- essas duas alternativas puxam fonte/itálico
            # errados do tema do documento (bug real observado: um título
            # gerado por outra via saiu em Segoe UI Bold ITÁLICO, quando
            # deveria ser só negrito). O tab herda o mesmo rpr do título,
            # sem itálico, então não tem como repetir esse problema.
            # IMPORTANTE: <w:tabs> vem ANTES de <w:spacing> no schema.
            ppr = ('<w:keepNext/><w:tabs><w:tab w:val="right" w:pos="8504" w:leader="heavy"/></w:tabs>'
                   '<w:spacing w:before="360" w:after="240"/><w:jc w:val="both"/>') + rpr
            conteudo += '<w:r>%s<w:tab/></w:r>' % rpr
        else:
            ppr = '<w:keepNext/><w:spacing w:before="360" w:after="240"/><w:jc w:val="both"/>' + rpr
        return para(ppr, conteudo)

    if t == "subtitulo":
        # Espaço antes > depois (princípio de proximidade: o título deve
        # ficar visualmente colado ao texto que introduz, não ao anterior
        # -- Robbins, "Painting with Print"; já seguido por "titulo" acima,
        # faltava aqui).
        rpr = "<w:rPr>%s<w:b/><w:bCs/></w:rPr>" % FONT
        ppr = '<w:keepNext/><w:spacing w:before="240" w:after="120"/><w:jc w:val="both"/>' + rpr
        return para(ppr, runs(texto, rpr))

    if t == "paragrafo":
        rpr = "<w:rPr>%s<w:sz w:val=\"22\"/><w:szCs w:val=\"22\"/></w:rPr>" % FONT
        ppr = '<w:spacing w:before="0" w:after="240"/><w:jc w:val="both"/>' + rpr
        return para(ppr, runs(texto, rpr))

    if t == "citacao":
        # Citação longa de ementa/doutrina/decisão reproduzida em parágrafo
        # dedicado, com recuo próprio: ENTRE ASPAS (automático), SEM
        # itálico (regra do usuário, ago/2026 -- 3ª correção sobre este
        # ponto: 1ª versão exigia itálico, foi corrigida para sem itálico,
        # depois corrigida de novo para com itálico, e agora corrigida uma
        # 3ª vez, desta vez definitivamente para SEM itálico -- "não deixe
        # em itálico o que é citação direta com recuo e parágrafo próprio".
        # Fica valendo esta última: o recuo + as aspas já bastam para
        # marcar a transcrição; o itálico ficava redundante.).
        # Recuo de 1cm (567 twips). Aspas são aplicadas automaticamente ao
        # redor de "texto" se ele ainda não vier com elas -- não depender de
        # o autor lembrar de digitar aspas manualmente.
        #
        # "atribuicao" (opcional): referência ao final -- "(Parecer nº
        # 10.452/2026, id. 36004312, 29/07/2026)", "(STJ, REsp .../SP,
        # Rel. Min. Fulano, j. .../.../....)" -- fica FORA das aspas,
        # depois delas, no mesmo parágrafo/estilo. Não é texto citado, é
        # referência bibliográfica. Achado comparando com uma peça real
        # ajustada pelo usuário (ago/2026): se a atribuição for concatenada
        # dentro de "texto", o auto-quote acima ia botar aspas em volta dela
        # também (errado) -- por isso um campo à parte, nunca dentro das aspas.
        #
        # Citação CURTA/inline dentro de um `paragrafo` corrente continua
        # em itálico, marcada manualmente com *asteriscos* pelo autor (ver
        # SKILL.md) -- essa regra não muda, só a do bloco `citacao` (com
        # recuo e parágrafo próprio) é que perdeu o itálico.
        #
        # Dispositivo legal (artigo de lei/código): NÃO tem campo próprio
        # no bloco `citacao` (existiu um campo "dispositivo" por poucas
        # horas, ago/2026, removido no mesmo dia a pedido do usuário --
        # "é melhor não colocar o CPC, seguido do dispositivo"). A norma
        # citada vai num `paragrafo` ANTES do bloco `citacao` ("Dispõe o
        # art. 1º do CPC:"), e o bloco `citacao` recebe só a transcrição
        # literal, sem prefixo -- mesmo padrão de introduzir uma ementa/
        # decisão com um parágrafo antes (ver SKILL.md).
        texto_c = texto.strip()
        ABRE, FECHA = ('"', '“', '«'), ('"', '”', '»')
        if not (texto_c.startswith(ABRE) and texto_c.endswith(FECHA)):
            texto_c = '"%s"' % texto_c
        atribuicao = b.get("atribuicao", "").strip()
        # 10,5pt (sz 21) -- regra do usuário, ago/2026 (era 10pt/sz 20).
        rpr = "<w:rPr>%s<w:sz w:val=\"21\"/><w:szCs w:val=\"21\"/></w:rPr>" % FONT
        ppr = ('<w:spacing w:before="80" w:after="80"/><w:ind w:left="567"/>'
               '<w:jc w:val="both"/>') + rpr
        conteudo = runs(texto_c, rpr)
        if atribuicao:
            conteudo += runs(" " + atribuicao, rpr)
        return para(ppr, conteudo)

    if t == "pedido":
        return pedido(b)

    if t == "caixa_destaque":
        return caixa_destaque(b)

    if t == "tabela":
        return tabela(b)

    if t == "espaco":
        rpr = "<w:rPr>%s<w:sz w:val=\"22\"/><w:szCs w:val=\"22\"/></w:rPr>" % FONT
        ppr = '<w:spacing w:before="0" w:after="240"/><w:jc w:val="both"/>' + rpr
        return para(ppr, "")

    if t == "quebra_pagina":
        # útil para separar documentos anexados dentro do mesmo DOCX/PDF
        # (ex.: petição + demonstrativo de cálculo num único arquivo).
        # w:spacing before/after=0 explícito: sem isso, este parágrafo (só
        # o \b da quebra, sem texto) herda o espaçamento padrão do estilo
        # Normal do documento, que soma ao w:before do título seguinte e
        # cria um vão visível no topo de cada capítulo novo -- bug real
        # visto ao pular capítulos num documento longo (ago/2026).
        rpr = "<w:rPr>%s<w:sz w:val=\"22\"/><w:szCs w:val=\"22\"/></w:rPr>" % FONT
        ppr = '<w:spacing w:before="0" w:after="0"/>' + rpr
        return '<w:p><w:pPr>%s</w:pPr><w:r>%s<w:br w:type="page"/></w:r></w:p>' % (ppr, rpr)

    if t == "fecho":
        return fecho(b)

    raise ValueError("tipo de bloco desconhecido: %r" % t)


def cap_primeira_letra(texto):
    """Maiuscula a 1ª letra de verdade do texto, pulando marcação
    markdown/pontuação na frente (**negrito, *itálico, "aspas, etc.) --
    não usar texto[0].upper() ingênuo, que maiusculizaria o "*" (no-op)
    e deixaria a palavra real intocada."""
    m = re.search(r'[a-zA-ZÀ-ÖØ-öø-ÿ]', texto)
    if not m:
        return texto
    i = m.start()
    return texto[:i] + texto[i].upper() + texto[i + 1:]


def pedido(b):
    """Item de pedido: marcador em negrito + recuo deslocado (hanging), de
    modo que as linhas seguintes (e o texto após o marcador) alinhem numa
    coluna própria. Valores calibrados por medição direta das coordenadas
    do PDF de referência (agravo "com tipografia"):
    nivel 1 (A./B./C.): marcador a 363 twips da margem, texto a 570 twips
      -> ind left=570 hanging=207.
    nivel 2 (b.1)/b.2), subitens): marcador a 427 twips, texto a 831 twips
      -> ind left=831 hanging=404.
    Regra do usuário (set/2026): o texto do pedido SEMPRE começa com
    letra maiúscula -- aplicado automaticamente aqui (não depender de
    quem escreve o JSON lembrar); ver `cap_primeira_letra`."""
    marcador = b.get("marcador", "a)")
    texto = cap_primeira_letra(b.get("texto", ""))
    nivel = int(b.get("nivel", 1))
    left, hanging = (720, 357) if nivel == 1 else (1050, 625)
    rpr = "<w:rPr>%s<w:sz w:val=\"22\"/><w:szCs w:val=\"22\"/></w:rPr>" % FONT
    rpr_b = rpr.replace("</w:rPr>", "<w:b/><w:bCs/></w:rPr>")
    # tab stop explícito em "left": sem isso, o \t após o marcador vira um
    # salto mínimo (não necessariamente até o recuo) e marcadores mais
    # largos que "A." (como "b.1)") colidem com o início do texto.
    # IMPORTANTE: dentro de <w:pPr> a ordem dos elementos é fixada pelo
    # schema do OOXML — <w:tabs> deve vir ANTES de <w:spacing>, senão o
    # Word ignora o tab silenciosamente (só descobri isso comparando com
    # a ordem real usada no documento de referência).
    ppr = ('<w:tabs><w:tab w:val="left" w:pos="%d"/></w:tabs>'
           '<w:spacing w:before="0" w:after="240"/>'
           '<w:ind w:left="%d" w:hanging="%d"/>'
           '<w:jc w:val="both"/>' % (left, left, hanging)) + rpr
    marca = '<w:r>%s<w:t xml:space="preserve">%s\t</w:t></w:r>' % (rpr_b, esc(marcador))
    return para(ppr, marca + runs(texto, rpr))


def caixa_destaque(b):
    """Quadro de destaque: célula azul-marinho à esquerda com título em
    branco (centralizado na vertical) + célula cinza à direita com lista de
    marcadores. Réplica fiel do elemento de 'tipografia' das peças do
    escritório. Usa numId 24 (bullet Symbol) e estilo Tabelacomgrade, ambos
    presentes no template. cantSplit na linha impede que a caixa quebre
    entre páginas deixando um retângulo azul órfão sem título do outro
    lado — mesmo problema e mesma correção documentados em tabela()."""
    titulo = b.get("titulo", "")
    itens = b.get("itens", [])

    rpr_branco = ('<w:rPr>%s<w:b/><w:bCs/>'
                  '<w:color w:val="FFFFFF" w:themeColor="background1"/>'
                  '<w:sz w:val="28"/><w:szCs w:val="28"/></w:rPr>' % FONT)
    titulo_p = para('<w:spacing w:before="0" w:after="0"/>' + rpr_branco,
                    '<w:r>%s<w:t>%s</w:t></w:r>' % (rpr_branco, esc(titulo)))
    # vAlign=center faz o Word centralizar de verdade, adaptando-se à altura
    # real da caixa (que varia com o nº/tamanho dos itens da célula cinza).
    # A versão anterior usava 3 parágrafos vazios em vez disso — um recuo
    # fixo que só "parecia" centralizado para a quantidade específica de
    # itens do documento original; com menos/mais itens o título ficava
    # visivelmente deslocado para baixo ou para cima.
    navy_cell = (
        '<w:tc><w:tcPr><w:tcW w:w="2122" w:type="dxa"/>'
        '<w:tcBorders><w:right w:val="nil"/></w:tcBorders>'
        '<w:shd w:val="clear" w:color="auto" w:fill="%s" w:themeFill="text2"/>'
        '<w:vAlign w:val="center"/></w:tcPr>%s</w:tc>'
        % (NAVY, titulo_p))

    rpr_item = "<w:rPr>%s<w:sz w:val=\"22\"/><w:szCs w:val=\"22\"/></w:rPr>" % FONT
    itens_xml = ""
    for it in itens:
        ppr = ('<w:numPr><w:ilvl w:val="0"/><w:numId w:val="24"/></w:numPr>'
               '<w:spacing w:before="0" w:after="240"/><w:ind w:left="466"/>'
               '<w:jc w:val="both"/>') + rpr_item
        itens_xml += para(ppr, runs(it, rpr_item))
    gray_cell = (
        '<w:tc><w:tcPr><w:tcW w:w="6372" w:type="dxa"/>'
        '<w:tcBorders><w:top w:val="nil"/><w:left w:val="nil"/>'
        '<w:bottom w:val="nil"/><w:right w:val="nil"/></w:tcBorders>'
        '<w:shd w:val="clear" w:color="auto" w:fill="%s" w:themeFill="background1"/>'
        '</w:tcPr>%s</w:tc>' % (GRAY, itens_xml))

    tbl = (
        '<w:tbl><w:tblPr><w:tblStyle w:val="Tabelacomgrade"/>'
        '<w:tblW w:w="0" w:type="auto"/>'
        '<w:tblLook w:val="04A0" w:firstRow="1" w:lastRow="0" w:firstColumn="1"'
        ' w:lastColumn="0" w:noHBand="0" w:noVBand="1"/></w:tblPr>'
        '<w:tblGrid><w:gridCol w:w="2122"/><w:gridCol w:w="6372"/></w:tblGrid>'
        '<w:tr><w:trPr><w:cantSplit/></w:trPr>%s%s</w:tr></w:tbl>' % (navy_cell, gray_cell))
    # SEM parágrafo em branco depois da tabela (regra do usuário, set/2026
    # -- havia um antes, "respiro" pra não colar no texto seguinte, mas
    # isso criava um bug real: quando a caixa cabe bem no fim da página 1,
    # esse parágrafo vazio -- que tem altura de linha própria, sempre,
    # mesmo sem texto -- "sobra" sozinho no topo da página 2, e some com
    # o "w:before" do título seguinte (que É suprimido no topo de página
    # pelo Word/LibreOffice quando é o 1º parágrafo da página, mas só se
    # não houver esse vazio antes dele) -- resultado: um vão grande e
    # vazio no início da página 2, bem visível. O respiro correto vem só
    # do `spacing w:before` do bloco seguinte (ex. `titulo` já tem 360
    # twips = 18pt antes) -- suficiente visualmente no caso normal, e
    # automaticamente suprimido pelo Word quando esse bloco cai no topo
    # de uma nova página, o que elimina o bug. `caixa_destaque` deve
    # sempre ser seguido por um bloco com espaçamento "before" próprio
    # (tipicamente `titulo`), nunca por um `paragrafo` colado sem folga.
    return tbl


def tabela(b):
    """Tabela de dados real (grade nativa), para comparar vários itens por
    vários critérios lado a lado -- diferente de caixa_destaque (lista de
    marcadores), que serve bem a poucos itens paralelos mas não a dados
    tabulares: cramar várias dimensões numa frase corrida por bullet
    obriga o leitor a "garimpar" cada linha para comparar uma coluna.
    Cabeçalho repete em toda página (tblHeader) e nenhuma linha quebra ao
    meio entre páginas (cantSplit), evitando a caixa "órfã" sem título que
    aparecia quando uma caixa_destaque longa demais estourava a página."""
    titulo = b.get("titulo", "")
    colunas = b.get("colunas", [])
    linhas = b.get("linhas", [])
    n = len(colunas)
    total = 8494
    larguras = list(b.get("larguras") or [total // n] * n)
    larguras[-1] += total - sum(larguras)
    # tabelas com muitas colunas (7+) apertam o texto e o Word quebra
    # palavras no meio (sem hífen, porque autoHyphenation está desligado
    # no template — ver nota sobre o bug "advo-/-ado"). Nesses casos passe
    # "tamanho_fonte" menor (ex. 16 = 8pt) e/ou "larguras" calibradas.
    sz = str(b.get("tamanho_fonte", 21))
    # colunas numéricas (R$, índices, %) devem alinhar à DIREITA -- senão
    # os dígitos não empilham por casa decimal entre as linhas e a tabela
    # parece "torta"/desalinhada. Default "esquerda" (rótulos/texto); passe
    # "alinhamentos": ["esquerda","direita",...] com "direita" em toda
    # coluna de valor monetário/numérico.
    JC = {"esquerda": "left", "direita": "right", "centro": "center"}
    alinhamentos = b.get("alinhamentos") or ["esquerda"] * n
    jcs = [JC.get(a, "left") for a in alinhamentos]

    rpr_corpo = "<w:rPr>%s<w:sz w:val=\"%s\"/><w:szCs w:val=\"%s\"/></w:rPr>" % (FONT, sz, sz)
    rpr_cabecalho = ('<w:rPr>%s<w:b/><w:bCs/>'
                      '<w:color w:val="FFFFFF" w:themeColor="background1"/>'
                      '<w:sz w:val="%s"/><w:szCs w:val="%s"/></w:rPr>' % (FONT, sz, sz))

    def celula(texto, largura, rpr, jc, fill=None):
        shd = ('<w:shd w:val="clear" w:color="auto" w:fill="%s"/>' % fill) if fill else ""
        ppr = ('<w:spacing w:before="40" w:after="40"/><w:jc w:val="%s"/>' % jc) + rpr
        p = para(ppr, runs(texto, rpr))
        # vAlign=center: linhas com célula de 1 linha ao lado de célula com
        # 2+ linhas (por quebra de texto) ficam com o conteúdo desnivelado
        # se o topo for a referência; centralizado verticalmente disfarça
        # a diferença de altura entre linhas de conteúdo desigual.
        return ('<w:tc><w:tcPr><w:tcW w:w="%d" w:type="dxa"/>%s'
                '<w:vAlign w:val="center"/></w:tcPr>%s</w:tc>' % (largura, shd, p))

    header_cells = "".join(
        celula(c, larguras[i], rpr_cabecalho, jcs[i], fill=NAVY) for i, c in enumerate(colunas))
    header_row = '<w:tr><w:trPr><w:cantSplit/><w:tblHeader/></w:trPr>%s</w:tr>' % header_cells

    body_rows = ""
    for idx, linha in enumerate(linhas):
        fill = GRAY if idx % 2 == 1 else None
        cells = "".join(
            celula(v, larguras[i], rpr_corpo, jcs[i], fill=fill) for i, v in enumerate(linha[:n]))
        body_rows += '<w:tr><w:trPr><w:cantSplit/></w:trPr>%s</w:tr>' % cells

    grid = "".join('<w:gridCol w:w="%d"/>' % w for w in larguras)
    # Bordas finas (0,5pt) cinza-neutro em toda a grade: linha real com
    # colunas alinhadas, não pseudo-tabela em bullets/tabs (Butterick,
    # "Typography for Lawyers" -- tables / grids of numbers).
    borda = 'w:sz="4" w:space="0" w:color="BFBFBF"'
    tbl_borders = (
        '<w:tblBorders>'
        '<w:top w:val="single" %s/><w:left w:val="single" %s/>'
        '<w:bottom w:val="single" %s/><w:right w:val="single" %s/>'
        '<w:insideH w:val="single" %s/><w:insideV w:val="single" %s/>'
        '</w:tblBorders>' % (borda, borda, borda, borda, borda, borda))
    tbl_cellmar = ('<w:tblCellMar><w:top w:w="80" w:type="dxa"/><w:left w:w="100" w:type="dxa"/>'
                   '<w:bottom w:w="80" w:type="dxa"/><w:right w:w="100" w:type="dxa"/></w:tblCellMar>')
    tbl = (
        '<w:tbl><w:tblPr><w:tblStyle w:val="Tabelacomgrade"/>'
        '<w:tblW w:w="0" w:type="auto"/>%s%s'
        '<w:tblLook w:val="04A0" w:firstRow="1" w:lastRow="0" w:firstColumn="1"'
        ' w:lastColumn="0" w:noHBand="0" w:noVBand="1"/></w:tblPr>'
        '<w:tblGrid>%s</w:tblGrid>%s%s</w:tbl>'
        % (tbl_borders, tbl_cellmar, grid, header_row, body_rows))

    saida = ""
    if titulo:
        rpr_t = "<w:rPr>%s<w:i/><w:iCs/><w:sz w:val=\"22\"/><w:szCs w:val=\"22\"/></w:rPr>" % FONT
        ppr_t = ('<w:pStyle w:val="TableCaption"/><w:keepNext/>'
                 '<w:spacing w:before="0" w:after="120"/><w:jc w:val="left"/>') + rpr_t
        saida += para(ppr_t, runs(titulo, rpr_t))
    saida += tbl
    rpr_e = "<w:rPr>%s<w:sz w:val=\"22\"/><w:szCs w:val=\"22\"/></w:rPr>" % FONT
    saida += para('<w:spacing w:before="0" w:after="240"/>' + rpr_e, "")
    return saida


def fecho(b):
    """Réplica exata da estrutura do agravo de referência: o fecho inteiro
    é uma tabela invisível (bordas suprimidas) de 2 colunas iguais
    (4247 twips cada, metade da largura útil). Linhas 1-3 têm as células
    mescladas (largura cheia): encerramento, data+assinatura, respiro.
    Linhas 4-5 usam as 2 colunas separadas: célula esquerda vazia,
    célula direita com nome/OAB — por isso ficam centralizados só na
    metade direita da página, sob a assinatura, e não na página inteira."""
    # A cidade do fecho é SEMPRE Porto Velho/RO (sede do escritório),
    # independentemente da comarca/tribunal do processo — nunca a cidade
    # do caso. Por isso o bloco aceita "data" (só a data) e monta
    # "Porto Velho/RO, {data}" sozinho; "cidade_data" continua aceito como
    # escape hatch bruto só para o raro caso de o usuário pedir outra coisa
    # explicitamente.
    if "cidade_data" in b:
        cidade_data = b["cidade_data"]
    else:
        data = b.get("data", "")
        cidade_data = "Porto Velho/RO, %s" % data if data else "Porto Velho/RO"
    nome = b.get("nome", "Roberto Grécia Bessa")
    oab = b.get("oab", "OAB/RO 7865")
    nome2 = b.get("nome2")
    oab2 = b.get("oab2")
    com_assinatura = b.get("assinatura", True)
    # "Pede provimento" só é correto para RECURSOS (agravo de instrumento,
    # apelação, recurso especial/extraordinário, agravo interno/
    # regimental) — são "providos" ou "desprovidos" pelo tribunal. Toda
    # petição que não é recurso (petição inicial, contestação, réplica,
    # cumprimento de sentença, requerimento, embargos de declaração) é
    # "deferida" ou "indeferida" pelo juízo, e fecha com "pede
    # deferimento". Não existe um default seguro entre os dois — por
    # isso não há mais valor implícito: ou vem "encerramento" explícito
    # (para casos fora do padrão, ex. "Atenciosamente," extrajudicial),
    # ou vem "recurso" (true/false) e o texto certo é montado sozinho.
    if "encerramento" in b:
        encerramento = b["encerramento"]
    elif "recurso" in b:
        encerramento = ("Nestes termos, pede provimento." if b["recurso"]
                         else "Nestes termos, pede deferimento.")
    else:
        raise ValueError(
            "bloco 'fecho' precisa de \"recurso\": true/false (recurso "
            "pede provimento; toda petição não-recursal pede "
            "deferimento) ou de \"encerramento\" explícito.")

    sty = '<w:pStyle w:val="1Pargrafo"/>'
    color = '<w:color w:val="000000" w:themeColor="text1"/>'
    sz21 = '<w:sz w:val="21"/><w:szCs w:val="21"/>'

    rpr_i = "<w:rPr><w:i/><w:iCs/>%s%s</w:rPr>" % (color, sz21)
    rpr_n = "<w:rPr>%s%s</w:rPr>" % (color, sz21)
    rpr_b = "<w:rPr><w:b/><w:bCs/>%s%s</w:rPr>" % (color, sz21)

    drawing = ""
    if com_assinatura and os.path.exists(SIG_DRAWING):
        sig = open(SIG_DRAWING, encoding="utf-8").read()
        drawing = '<w:r><w:rPr><w:noProof/>%s%s</w:rPr>%s</w:r>' % (color, sz21, sig)

    p_encerramento = para(sty + '<w:keepNext/><w:spacing w:before="120" w:after="0"/>' + rpr_i,
                          '<w:r>%s<w:t>%s</w:t></w:r>' % (rpr_i, esc(encerramento)))
    p_data = para(sty + '<w:keepNext/><w:spacing w:before="120" w:after="0"/>' + rpr_n,
                  drawing + '<w:r>%s<w:t>%s</w:t></w:r>' % (rpr_n, esc(cidade_data)))
    p_vazio_full = para(sty + '<w:keepNext/><w:spacing w:before="0" w:after="0"/>' + rpr_n, "")
    # Célula esquerda das linhas 4-5: vazia por padrão (só ocupa espaço,
    # "sem função visual" no fecho de assinatura única). Quando um segundo
    # signatário é informado (nome2/oab2 — ex.: co-advogado do caso), essa
    # mesma célula ganha nome/OAB centralizados na metade esquerda, sem
    # imagem de assinatura própria (a skill só tem a assinatura manuscrita
    # do Roberto embutida; o segundo nome identifica o co-signatário, a
    # assinatura eletrônica de fato vem de quem protocola no PJe).
    if nome2:
        p_esq_nome = para(sty + '<w:keepNext/><w:spacing w:before="40" w:after="40"/><w:jc w:val="center"/>' + rpr_b,
                           '<w:r>%s<w:t>%s</w:t></w:r>' % (rpr_b, esc(nome2)))
    else:
        p_esq_nome = para(sty + '<w:keepNext/><w:spacing w:before="0" w:after="0"/><w:jc w:val="right"/>' + rpr_b, "")
    p_nome = para(sty + '<w:keepNext/><w:spacing w:before="40" w:after="40"/><w:jc w:val="center"/>' + rpr_b,
                  '<w:r>%s<w:t>%s</w:t></w:r>' % (rpr_b, esc(nome)))
    if oab2:
        p_esq_oab = para(sty + '<w:spacing w:before="0" w:after="0"/><w:jc w:val="center"/>' + rpr_n,
                          '<w:r>%s<w:t>%s</w:t></w:r>' % (rpr_n, esc(oab2)))
    else:
        p_esq_oab = para(sty + '<w:spacing w:before="0" w:after="0"/><w:jc w:val="right"/>' + rpr_n, "")
    p_oab = para(sty + '<w:spacing w:before="0" w:after="0"/><w:jc w:val="center"/>' + rpr_n,
                 '<w:r>%s<w:t>%s</w:t></w:r>' % (rpr_n, esc(oab)))

    def celula(w, conteudo, span=False):
        span_tag = '<w:gridSpan w:val="2"/>' if span else ""
        return '<w:tc><w:tcPr><w:tcW w:w="%d" w:type="dxa"/>%s</w:tcPr>%s</w:tc>' % (w, span_tag, conteudo)

    linha_full = lambda conteudo: '<w:tr>%s</w:tr>' % celula(8494, conteudo, span=True)
    linha_dupla = lambda esq, dir_: '<w:tr>%s%s</w:tr>' % (celula(4247, esq), celula(4247, dir_))

    tbl = (
        '<w:tbl><w:tblPr><w:tblStyle w:val="Tabelacomgrade"/>'
        '<w:tblW w:w="0" w:type="auto"/>'
        '<w:tblBorders><w:top w:val="none" w:sz="0" w:space="0" w:color="auto"/>'
        '<w:left w:val="none" w:sz="0" w:space="0" w:color="auto"/>'
        '<w:bottom w:val="none" w:sz="0" w:space="0" w:color="auto"/>'
        '<w:right w:val="none" w:sz="0" w:space="0" w:color="auto"/>'
        '<w:insideH w:val="none" w:sz="0" w:space="0" w:color="auto"/>'
        '<w:insideV w:val="none" w:sz="0" w:space="0" w:color="auto"/></w:tblBorders>'
        '<w:tblCellMar><w:left w:w="0" w:type="dxa"/><w:right w:w="0" w:type="dxa"/></w:tblCellMar>'
        '<w:tblLook w:val="04A0" w:firstRow="1" w:lastRow="0" w:firstColumn="1"'
        ' w:lastColumn="0" w:noHBand="0" w:noVBand="1"/></w:tblPr>'
        '<w:tblGrid><w:gridCol w:w="4247"/><w:gridCol w:w="4247"/></w:tblGrid>'
        + linha_full(p_encerramento)
        + linha_full(p_data)
        + linha_full(p_vazio_full)
        + linha_dupla(p_esq_nome, p_nome)
        + linha_dupla(p_esq_oab, p_oab)
        + '</w:tbl>')
    return tbl


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    cfg = json.load(open(sys.argv[1], encoding="utf-8"))
    output = cfg["output"]
    base_dir = os.path.dirname(os.path.abspath(sys.argv[1]))

    # Gate do mapa (obrigatório, anterior ao lint de citações): recusa gerar
    # se o mapa do caso (mapa-de-caso) tem pendência 🔴/⏰ sem decisão do
    # advogado. Ver gate_mapa.py e SKILL.md ("Quando vem de um mapa de caso").
    erros_mapa, avisos_mapa = checar_pendencias_mapa(cfg, base_dir=base_dir)
    for a in avisos_mapa:
        sys.stderr.write("aviso: " + a + "\n")
    if erros_mapa:
        sys.stderr.write("Peça NÃO gerada:\n")
        for e in erros_mapa:
            sys.stderr.write("  " + e + "\n")
        sys.exit(3)

    # Lint de citações (obrigatório): toda citação de julgado precisa de ficha
    # verificada em "precedentes"; relator/data/órgão e o que está entre aspas
    # são conferidos contra a ficha. Erros reais de set/2026 motivaram isso —
    # ver lint_citacoes.py e SKILL.md ("Citações verificadas"). Só
    # "permitir_nao_verificado": true rebaixa os erros a aviso.
    relatorio = lint(cfg, base_dir=base_dir)
    sys.stderr.write(relatorio.texto() + "\n")
    if relatorio.erros:
        sys.stderr.write("Peça NÃO gerada: citação sem ficha ou divergente da ficha (acima). "
                         "Corrija a peça ou as fichas; \"permitir_nao_verificado\": true só em último caso.\n")
        sys.exit(2)

    _LINKS.update(carregar_links(cfg, base_dir))
    body_xml = "".join(bloco(b) for b in cfg["blocks"])
    sys.stderr.write("Links do inteiro teor na peça: %d julgado(s) com link oficial\n" % len(_RELS))

    zin = zipfile.ZipFile(TEMPLATE)
    doc = zin.read("word/document.xml").decode("utf-8")
    root = re.match(r"(.*?<w:body>)", doc, re.S).group(1)
    sect = re.search(r"<w:sectPr.*?</w:sectPr>", doc, re.S).group(0)
    new_doc = root + body_xml + sect + "</w:body></w:document>"
    rels = zin.read("word/_rels/document.xml.rels").decode("utf-8")
    if _RELS:
        rels = rels.replace("</Relationships>", "".join(
            '<Relationship Id="%s" Type="%s" Target="%s" TargetMode="External"/>'
            % (rid, REL_HYPERLINK, esc(url).replace('"', "&quot;")) for url, rid in _RELS.items())
            + "</Relationships>")

    os.makedirs(os.path.dirname(os.path.abspath(output)) or ".", exist_ok=True)
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.namelist():
            if item == "word/document.xml":
                zout.writestr(item, new_doc)
            elif item == "word/_rels/document.xml.rels":
                zout.writestr(item, rels)
            else:
                zout.writestr(item, zin.read(item))
    zin.close()
    print("OK: %s (%d bytes)" % (output, os.path.getsize(output)))


if __name__ == "__main__":
    main()
