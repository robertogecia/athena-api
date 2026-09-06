---
name: peticao-rg
description: >-
  Gera o documento final em DOCX/PDF com o papel timbrado e a formatação
  padrão do escritório Roberto Grécia (logo no cabeçalho da 1ª página,
  rodapé azul com contatos, numeração de páginas, Segoe UI 11pt justificado,
  assinatura manuscrita). Use quando o pedido for produzir ou formatar o
  documento em si — "passar a limpo", "timbrado", "no modelo do escritório",
  "com a formatação padrão", ou gerar o DOCX/PDF de texto já redigido, mesmo
  sem citar a palavra "petição". Use direto para o que não depende de
  análise de autos: procuração, substabelecimento, contrato, notificação
  extrajudicial, declaração, ofício e demais peças de mero expediente
  (juntada, habilitação). Para peça contenciosa de um caso com autos ou
  documentos (inicial, contestação, réplica, recurso, agravo, embargos,
  parecer) ainda não redigida, o mapa-de-caso vem primeiro e decide o
  conteúdo — esta skill entra depois, partindo do mapa. Se o texto já
  estiver redigido, entra sozinha; "gera o DOCX timbrado" de peça ainda não
  escrita não dispensa o mapa.
---

# Petição no modelo Roberto Grécia

Gera DOCX (e PDF) idêntico ao modelo do escritório: timbre, rodapé,
numeração, fontes embutidas e estilo de parágrafo são herdados de um
template extraído de uma peça real "com tipografia" (agravo de instrumento
da Esther) — nunca recriados à mão. Além dos blocos de texto, reproduz os
elementos de destaque que dão o acabamento profissional: **caixa de
destaque** (quadro azul-marinho + lista) e **pedidos** com marcador em
negrito e recuo deslocado.

## Fluxo

0. **É peça contenciosa? Procure o mapa antes de escrever qualquer linha.**
   Inicial, contestação, réplica, reconvenção, impugnação, recurso, parecer e
   afins: dê um `ls` na pasta do caso atrás do mapa do `mapa-de-caso`
   (`mapa-do-caso.md`, `mapa*.md`) e leia a seção "Quando vem de um mapa de
   caso" antes de continuar — vale mesmo que o pedido tenha chegado como
   "gera o DOCX timbrado". **Não achou mapa? Pergunte**: "não localizei mapa
   deste caso — quer que eu rode o `mapa-de-caso` primeiro, ou redijo
   direto?". Nunca leia "não achei" como autorização para redigir do zero —
   é exatamente aí que sai peça bonita e sem lastro. Documento que não é peça
   contenciosa (procuração, contrato, notificação, mero expediente) pula
   direto para o passo 1.
1. Redija o conteúdo da peça — a partir do mapa, se houver (o mérito jurídico
   é seu trabalho normal; esta skill cuida da forma).
2. Monte um JSON de blocos (formato abaixo) e salve em arquivo temporário.
   **Veio de mapa? Antes de montar o JSON**, confirme que nenhum item 🔴, ⏰,
   🟡 ou `[CARECE DE PRECEDENTE]` ficou sem decisão do advogado.
3. Gere o DOCX:
   ```bash
   python3 <skill>/scripts/build_docx.py entrada.json
   ```
4. Se o usuário quiser PDF (ou for protocolar):
   ```bash
   <skill>/scripts/docx2pdf.sh "Peticao.docx"
   ```
   Usa LibreOffice se houver; senão, Microsoft Word via AppleScript (na
   primeira vez o macOS pode pedir permissão de automação — avise o usuário).
5. Confira o resultado (abra o PDF ou renderize a 1ª página com
   `qlmanage -t -s 1400 -o <dir> arquivo.pdf`) antes de entregar.

Salve o arquivo na pasta que o usuário indicar (ou na pasta do caso), com
nome no padrão **`<Tipo de Peça> - <Cliente>.docx`** — o tipo da peça vem
primeiro, depois o nome do cliente. Exemplos: `Petição Inicial -
Alvaro.docx`, `Apelação - Esther.docx`, `Embargos Declaratórios -
João.docx`, `Agravo de Instrumento - Maria.pdf`. Use o tipo de peça por
extenso e legível (não abreviado), e o primeiro nome (ou nome usual) do
cliente, como o usuário já se refere a ele na conversa.

## Quando vem de um mapa de caso

Se a skill `mapa-de-caso` rodou antes (mapa salvo na pasta do caso ou montado
na conversa), ele é a fonte do conteúdo — não reescreva do zero:

- **Dos Fatos** sai da cronologia do mapa, na ordem das datas, cada fato com a
  prova citada por arquivo e folhas.
- **Do Direito** sai da matriz de amarração: um bloco por pedido, subindo tese
  → fato → prova → precedente verificado.
- **Pedidos** saem dos nós `PD`, na ordem de dependência lógica.

**PARE antes de gerar se o mapa deixou qualquer coisa para resolver antes do
protocolo** — não só o que está marcado 🔴, mas também prazo e preclusão (⏰),
tese em 🟡 que dependa de decisão sua, e `[CARECE DE PRECEDENTE]` em aberto. Diga quais são, explique o que cada uma muda no
documento, e pergunte antes de montar o JSON. Não é formalidade: uma reconvenção
que precluiu, ou uma peça que alega vício oculto e avaria aparente ao mesmo
tempo, custa o caso — e o DOCX timbrado sai igualmente bonito nos dois casos.

Liste **item a item**, cada um com o que muda no documento, e colha a resposta
do advogado **por item** — um "pode gerar" global não é decisão informada, é o
portão sendo cumprido por fora.

Se ele mandar gerar assim mesmo, **gere — e deixe a pendência visível no
documento entregue**, não só na conversa: o trecho afetado sai marcado (ex.:
"[PENDENTE: confirmar se a avaria era aparente]") e você repete a lista na
mensagem de entrega, dizendo que o arquivo não é versão de protocolo.

**Pendência de prazo não se resolve com marcador.** Um "[PENDENTE]" dentro da
contestação não preserva uma reconvenção que tinha de ser oferecida no mesmo
ato, nem uma preliminar que precluiu — o documento sai marcado e o direito
morre igual. Para item ⏰ só existem duas saídas: redigir agora o que precisa
ser apresentado junto, ou o advogado dizer, por escrito, que está abrindo mão.
Não ofereça a terceira.

Tese que o mapa marcou como pendente de pesquisa entra na peça marcada como
pendente, ou não entra. Nunca preencha o "Do Direito" com jurisprudência
lembrada de memória: número de processo, súmula ou tema só entram se vieram de
pesquisa desta sessão. Quando a matriz vier com `[CARECE DE PRECEDENTE]`, há
duas saídas legítimas e nenhuma terceira: rodar a pesquisa antes de redigir, ou
redigir sobre lei e doutrina declarando a jurisprudência pendente — ofereça as
duas ao advogado.

## Formato do JSON

```json
{
  "output": "/caminho/Tipo de Peca - Cliente.docx",
  "blocks": [
    {"tipo": "enderecamento", "texto": "EXCELENTÍSSIMO(A) SENHOR(A) DOUTOR(A) JUIZ(A) DE DIREITO DA ___ VARA CÍVEL DA COMARCA DE ___, ESTADO DE ___"},
    {"tipo": "processo", "texto": "Processo nº 0000000-00.0000.0.00.0000"},
    {"tipo": "espaco"},
    {"tipo": "paragrafo", "texto": "**NOME DA PARTE**, nacionalidade, estado civil, profissão, RG, CPF, endereço, por intermédio do advogado que esta subscreve, vem apresentar **CONTESTAÇÃO**, pelas razões a seguir."},
    {"tipo": "titulo", "texto": "I. Síntese da demanda"},
    {"tipo": "paragrafo", "texto": "Texto justificado; use **negrito**, *itálico* e __sublinhado__ inline."},
    {"tipo": "caixa_destaque",
     "titulo": "RAZÕES PARA CONCESSÃO DA LIMINAR",
     "itens": ["Primeiro ponto, curto e direto.", "Segundo ponto.", "Terceiro ponto."]},
    {"tipo": "subtitulo", "texto": "II.1. Da preliminar tal"},
    {"tipo": "citacao", "texto": "Citação longa de doutrina/jurisprudência — recuo de 2,5cm, fonte 10pt."},
    {"tipo": "titulo", "texto": "V. Dos pedidos"},
    {"tipo": "paragrafo", "texto": "Ante o exposto, requer-se:"},
    {"tipo": "pedido", "marcador": "A.", "texto": "primeiro pedido;"},
    {"tipo": "pedido", "marcador": "B.", "texto": "segundo pedido, com desdobramentos:"},
    {"tipo": "pedido", "marcador": "b.1)", "nivel": 2, "texto": "subitem do pedido B;"},
    {"tipo": "fecho", "data": "1º de julho de 2026", "recurso": true, "nome": "Roberto Grécia Bessa", "oab": "OAB/RO 7865", "assinatura": true}
  ]
}
```

Tipos de bloco:
- `enderecamento` — 12pt negrito. Aceita caixa-alta ("EXCELENTÍSSIMO...
  JUIZ...") para 1ª instância ou Title Case ("Ao Egrégio Tribunal de
  Justiça...") para tribunal.
- `processo` — itálico, 11pt.
- `paragrafo` — corpo justificado 11pt; marcação inline **negrito**,
  *itálico*, __sublinhado__.
- `titulo` — seção (I., II., ...), 14pt negrito. Aceita `"linha": true`
  para uma régua horizontal sólida após o texto, preenchendo até a
  margem direita (estilo visto no 1º título de alguns agravos "com
  tipografia"). Use com moderação — normalmente só no primeiro título
  (ex.: "Resumo do Agravo"), não em todos. **Só em peça processual**: em
  documento destinado ao cliente (ver "Documentos para o cliente"
  abaixo), nunca use — o usuário mandou tirar (jul/2026), a régua fica
  parecendo um campo a preencher e o título do documento não é uma seção.
- `subtitulo` — subseção (II.1., ...), 12pt negrito.
- `citacao` — citação longa recuada, 10pt.
- `caixa_destaque` — **quadro de destaque** (o elemento "tipografado" das
  peças do escritório): faixa azul-marinho à esquerda com `titulo` em
  branco + lista de `itens` (marcadores) na área cinza. Use para os
  pontos-chave da liminar/tutela ou uma síntese em bullets. Cada item
  aceita marcação inline.
- `pedido` — item de pedido com `marcador` em **negrito** e recuo
  deslocado (as linhas seguintes alinham sob o texto). `nivel: 2` recua
  mais (para subitens tipo `b.1)`). Prefira este bloco a parágrafos
  "a) ..." soltos — é o padrão visual das peças recentes.
- `tabela` — **grade de dados real** (bordas finas, cabeçalho azul-marinho
  com texto branco, zebra striping nas linhas). Use para comparar vários
  itens por vários critérios lado a lado — planilha de cálculo, quadro
  comparativo, cronologia tabular. Diferente de `caixa_destaque` (que é
  para poucos pontos em bullets, não dados tabulares). Formato:
  `{"tipo": "tabela", "titulo": "legenda opcional acima", "colunas": ["Verba", "Principal", "Total"], "alinhamentos": ["esquerda", "direita", "direita"], "linhas": [["Caução", "R$ 6.400,00", "R$ 7.862,53"], ["Total", "R$ 9.400,00", "R$ 11.367,51"]]}`.
  **`alinhamentos`** (lista de `"esquerda"`/`"direita"`/`"centro"`, um por
  coluna) — SEMPRE passe isso quando alguma coluna tiver valores
  monetários, índices, percentuais ou qualquer número que faça sentido
  comparar entre linhas: marque essas colunas como `"direita"`, senão os
  dígitos não empilham por casa decimal entre as linhas e a tabela fica
  com aparência "torta"/desalinhada. Colunas de texto/rótulo (nome da
  verba, datas por extenso, período) ficam `"esquerda"`. Sem esse
  parâmetro, tudo cai em `"esquerda"` por padrão — evite depender do
  padrão em qualquer tabela com números.
  `larguras` (opcional, lista de twips por coluna) para controlar
  proporções; sem isso, distribui igualmente. Cabeçalho repete em toda
  página e nenhuma linha quebra ao meio entre páginas. Tabelas com muitas
  colunas (7+) ficam apertadas em fonte padrão (10,5pt) — o Word quebra
  palavra no meio sem hífen quando a coluna é mais estreita que a palavra
  (autoHyphenation está desligado no template). Para 7+ colunas, sempre:
  (1) abrevie cabeçalhos longos ("Índice inicial" → "Índice ini."),
  (2) passe `"tamanho_fonte": 16` (8pt, em half-points) para dar mais
  espaço, e (3) calibre `"larguras"` dando mais twips às colunas com
  conteúdo mais longo. Depois de gerar, sempre confira a página renderizada
  — se ainda houver palavra quebrada no meio, aumente a largura daquela
  coluna específica ou reduza mais o `tamanho_fonte`.
- `quebra_pagina` — força nova página. Use para separar documentos dentro
  do mesmo arquivo (ex.: petição + demonstrativo de cálculo anexado no
  mesmo PDF).
- `espaco` — linha em branco.
- `fecho` — bloco final completo (encerramento + data + assinatura
  manuscrita + nome/OAB). Passe só `"data": "1º de julho de 2026"` — o
  bloco já monta "Porto Velho/RO, {data}" sozinho (ver regra abaixo sobre
  a cidade). Omita `"assinatura": true` só se pedirem sem assinatura.
  **Não tem default de encerramento — é obrigatório escolher.** Passe
  `"recurso": true` (peça é recurso → "Nestes termos, pede provimento.")
  ou `"recurso": false` (peça não é recurso → "Nestes termos, pede
  deferimento."); ver a regra "provimento vs. deferimento" abaixo. Para
  fórmulas fora desse padrão (extrajudicial: "Atenciosamente,"), use
  `"encerramento"` com o texto exato em vez de `"recurso"`.

## Convenções da casa (extraídas das peças reais)

- Endereçamento (12pt negrito): caixa-alta para juízo de 1ª instância
  ("EXCELENTÍSSIMO... JUIZ...") ou Title Case para tribunal ("Ao Egrégio
  Tribunal de Justiça..."). Vai direto ao `Processo nº` (itálico) e um
  `espaco` antes da qualificação.
- Nome das partes em **negrito** na primeira menção (caixa-alta em 1ª
  instância; Title Case em recursos); nome da peça (CONTESTAÇÃO, AGRAVO...)
  em negrito dentro do parágrafo de qualificação — não como título.
- Seções numeradas no próprio texto do título: `I. Resumo`, `II. ...`;
  subseções como subtítulo: `II.1. Da...`.
- Estrutura típica: Resumo/Síntese → fundamentos por seção → Pedidos.
- **Pedidos**: use o bloco `pedido` (marcador em negrito + recuo deslocado),
  não parágrafos "a) ..." soltos. Marcadores no padrão das peças: `A.`,
  `B.`, `C.`... com subitens `b.1)`, `b.2)` (`nivel: 2`).
- **Resumo + caixa de destaque só em peça longa (5+ páginas estimadas).**
  Regra do usuário (jul/2026): esse padrão existe para dar a um julgador
  ocupado uma visão de 30 segundos de uma peça longa e complexa — numa
  peça curta (contestação simples, petição de poucos pedidos, menos de
  5 páginas no total) ele é redundante, porque a peça inteira já é rápida
  de ler. **Se estimar menos de 5 páginas, pule direto da qualificação
  para a primeira seção substantiva (`titulo` "I. Dos fatos" ou
  equivalente) — sem `titulo` "Resumo", sem os 3 parágrafos, sem
  `caixa_destaque`.** Estimativa prática: cada página comporta uns
  30-35 linhas de corpo; se a soma de todas as seções (fatos + direito +
  pedidos) ficar abaixo disso vezes 5, é peça curta. Na dúvida entre
  curta e longa, prefira omitir o resumo — errar pra menos é mais barato
  que uma peça curta com resumo redundante na frente.

  Quando a peça FOR longa (5+ páginas), a sequência do resumo é sempre:
  1. `titulo` "Resumo do Agravo" (ou "Síntese da demanda", conforme a
     peça) — **com `"linha": true`** (é o único título da peça que leva a
     régua).
  2. **No máximo 3 parágrafos curtos** resumindo a peça inteira em prosa:
     do que se trata, o que a decisão/parte contrária fez de errado, e
     por que a peça deve ser provida. Não é um resumo exaustivo com todos
     os fundamentos — é a versão de 30 segundos para quem só vai ler a
     primeira página. Se está saindo mais que 3 parágrafos ou parágrafos
     longos, é sinal de que fundamentação está vazando para o lugar
     errado; corte para o corpo da peça (seções I, II...).
  3. Um único `caixa_destaque`, **com exatamente 3 itens** (não 2, não 5)
     — os três motivos centrais pelos quais a peça deve ser aceita. Cada
     item é 1-2 frases, não um parágrafo. Título da caixa no padrão
     "RAZÕES PARA..." (CONCESSÃO DA LIMINAR / PROVIMENTO / REFORMA, etc.).
  O objetivo é que **endereçamento + qualificação + resumo + caixa caibam
  inteiros na página 1**. Isso normalmente funciona porque a qualificação
  ocupa uns 8-10 linhas, sobrando ~20-25 linhas de página 1 para o título
  + 3 parágrafos curtos + a caixa (que por si só ocupa uns 8-10 linhas
  com 3 itens). Se a qualificação for incomum (muitas partes, endereços
  longos), aperte ainda mais os parágrafos do resumo — a caixa de
  destaque nunca deve estourar pra página 2 sozinha, cortada ao meio.
  Depois de gerar, sempre confira a página 1 renderizada; se a caixa
  passou pra página 2, corte texto do resumo (não da caixa).
- Fecho: "Nestes termos, pede provimento." ou "..., pede deferimento." —
  já emitido pelo bloco `fecho` conforme `"recurso"`; não o escreva de
  novo como parágrafo.
- **"Provimento" vs. "deferimento" — nunca confundir.** "Provimento" é
  termo de julgamento de RECURSO (o tribunal/relator dá ou nega
  provimento a um recurso); "deferimento" é termo de decisão sobre
  PETIÇÃO/REQUERIMENTO (o juízo defere ou indefere um pedido). Usar
  "pede provimento" numa peça que não é recurso (ou vice-versa) é erro
  técnico visível para qualquer julgador.
  - **É recurso** (→ `"recurso": true`, "pede provimento"): agravo de
    instrumento, agravo interno/regimental, apelação, recurso especial,
    recurso extraordinário, embargos infringentes.
  - **Não é recurso** (→ `"recurso": false`, "pede deferimento"):
    petição inicial, contestação, réplica, cumprimento de sentença,
    impugnação ao cumprimento de sentença, embargos de declaração
    (é tecnicamente um recurso, mas na praxe da casa fecha como as
    demais petições — "pede deferimento" ou "pede acolhimento"),
    requerimento, manifestação.
  - Na dúvida sobre um tipo de peça não listado aqui, pergunte ao
    usuário antes de gerar — não adivinhe.
- **A cidade do fecho é SEMPRE Porto Velho/RO**, porque é onde fica o
  escritório e onde o advogado assina — independentemente de onde tramita
  o processo. Um agravo endereçado ao Tribunal de Justiça de outro
  estado, ou uma peça numa comarca como Fernandópolis/SP, ainda assim
  fecha com "Porto Velho/RO, {data}", nunca com a cidade do processo.
  Por isso passe só `"data"` no bloco `fecho` (não `"cidade_data"`) —
  a cidade já vem certa sozinha. Use `"cidade_data"` só se o usuário
  pedir expressamente uma cidade diferente.

## Documentos para o cliente (não para o juiz)

Termo de prestação de contas, contrato de honorários, recibo, declaração,
autorização — documentos que **o próprio cliente lê e assina**. As
convenções acima foram extraídas de peças processuais, dirigidas a juízes
e desembargadores; aqui o leitor é leigo, e várias delas se invertem:

- **Sem régua no título** (`"linha"` nunca). O título aqui nomeia o
  documento inteiro, não abre uma seção; a régua fica parecendo um campo
  a preencher.
- **Sem endereçamento e sem `processo` como cabeçalho de vara.** Se o
  documento se refere a um processo, cite-o no bloco `processo` de forma
  legível ("Processo nº 0000000-00.0000.0.00.0000, 4ª Vara Cível de Porto
  Velho/RO"), não como se estivesse peticionando.
- **Linguagem acessível, sem ser prolixa** — regra do usuário (jul/2026).
  Frases curtas, ordem direta, uma ideia por frase. Diga "o banco pagou",
  não "sobreveio a satisfação do débito". Corte "pelo presente
  instrumento particular", "ora prestado contas", "outrossim", "destarte",
  "consoante", "em face do exposto". Não troque precisão por simplicidade:
  o nome técnico da verba fica, mas **explicado uma vez em português**
  ("astreinte" → "multa que o juiz fixou para o caso de descumprimento").
  O artigo de lei vem entre parênteses no fim da frase, nunca abrindo o
  raciocínio.
- **Números por extenso só uma vez**, na primeira aparição de cada valor
  relevante. Repetir "(duzentos e sessenta e quatro mil...)" em toda
  menção polui e cansa.
- **Antecipe a dúvida do cliente em vez de deixá-la implícita.** Se o
  dinheiro caiu na conta do advogado, diga por quê. Se uma verba tem nome
  que sugere outra coisa, avise ("não é devolução do que foi descontado,
  é multa"). Esse parágrafo curto de esclarecimento vale mais que três de
  fundamentação.
- **Quadros (`tabela`) valem mais que prosa** para dinheiro. Um resumo
  final com "total do advogado" e "total do cliente" explícitos é
  obrigatório em prestação de contas.
- **Fecho**: use `"encerramento"` com texto próprio, nunca `"recurso"` —
  não se pede provimento nem deferimento a um cliente. Depois do bloco
  `fecho` (que assina o advogado), deixe dois `espaco` e os parágrafos de
  nome/qualificação do cliente para a assinatura dele.
  - **O `encerramento` precisa ocupar 2 linhas.** A assinatura manuscrita
    é uma imagem ancorada com deslocamento fixo dentro da tabela do
    fecho: com encerramento de 1 linha só, ela sobe e **encavala no
    texto** (bug real, jul/2026 — "Estando de acordo, as partes assinam
    este termo em duas vias iguais.", 68 caracteres, saiu riscado pela
    assinatura). Escreva algo com ~100+ caracteres, que quebre em duas
    linhas na largura útil: "Por estarem de acordo com tudo o que está
    escrito acima, as partes assinam este termo em duas vias iguais,
    ficando uma com cada uma delas." Sempre confira a página renderizada
    do fecho.
  - **Página de assinaturas**: ponha um `quebra_pagina` antes da última
    seção (a de aceite/quitação) para que ela e as duas assinaturas
    fiquem juntas numa página só. Sem isso, o bloco do cliente costuma
    cair sozinho na página seguinte, órfão da assinatura do advogado —
    ruim de ler e pior ainda no ZapSign.

## Regras importantes

- NUNCA edite `assets/template.docx` nem tente reconstruir o timbre com
  python-docx — o template carrega as fontes Segoe UI embutidas (não
  instaladas no macOS) e o rodapé desenhado; qualquer reconstrução perde
  fidelidade.
- NUNCA copie um documento de referência de um caso real (ex.: uma peça
  antiga de outro cliente que o usuário mencionou como "parecido com
  este") para servir de base do novo DOCX — mesmo que ele "pareça" o
  modelo certo. Ele carrega qualificação, fatos e pedidos do caso
  ANTERIOR; copiá-lo e apenas trocar o PDF final (sem reescrever
  `word/document.xml` inteiro via `build_docx.py`) produz um .docx que
  ainda contém o conteúdo do cliente errado, mesmo que o PDF exportado
  esteja correto. O único caminho para gerar o DOCX é `build_docx.py`
  a partir do `assets/template.docx` desta skill.
- O DOCX gerado tem ~8 MB por causa das fontes embutidas: é o esperado e
  garante renderização idêntica em qualquer máquina. O PDF sai leve.
- Detalhes completos da formatação (margens, tamanhos, espaçamentos, EMUs
  do logo/assinatura): leia `references/formatacao.md` — necessário apenas
  se precisar de um bloco que ainda não existe (imagem solta no corpo,
  numeração automática de lista, etc.).
- CUIDADO com "À" maiúsculo isolado (crase) no início de `enderecamento`
  em negrito — ex. "À Terceira Câmara Cível...". A fonte Segoe UI embutida
  no template é um SUBCONJUNTO (só contém os glifos usados nas peças de
  referência originais, que nunca começam com "À" maiúsculo — só "à"
  minúsculo em meio de frase, esse funciona normalmente). Ao converter
  para PDF via LibreOffice, esse "À" ausente do subconjunto é substituído
  por um glifo errado (visualmente parece um "W" solto antes do texto).
  Substitua por uma forma equivalente sem o "À" maiúsculo no início:
  "Colenda Terceira Câmara Cível..." ou "Ao Egrégio Tribunal de Justiça
  de Rondônia — Terceira Câmara Cível...". Sempre confira a 1ª página do
  PDF gerado quando o endereçamento for a um órgão colegiado (agravo
  interno/regimental), que é o caso típico em que se usa crase aqui.
