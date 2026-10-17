---
name: peticao-rg
description: >-
  Gera petições e peças jurídicas em DOCX/PDF com o papel timbrado e a
  formatação padrão do escritório Roberto Grécia (logo no cabeçalho da 1ª
  página, rodapé azul com contatos, numeração de páginas, Segoe UI 11pt
  justificado, assinatura manuscrita). Use SEMPRE que o usuário pedir para
  redigir, elaborar, formatar ou "passar a limpo" qualquer peça processual ou
  documento do escritório — contestação, petição inicial, réplica, recurso,
  agravo, embargos, parecer, notificação extrajudicial, procuração, contrato —
  ou quando pedir um DOCX/PDF "timbrado", "no modelo do escritório", "com a
  formatação padrão", mesmo sem citar a palavra "petição".
---

# Petição no modelo Roberto Grécia

Gera DOCX (e PDF) idêntico ao modelo do escritório: timbre, rodapé,
numeração, fontes embutidas e estilo de parágrafo são herdados de um
template extraído de um agravo de instrumento real do escritório "com
tipografia" — nunca recriados à mão. Além dos blocos de texto, reproduz os
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
   é seu trabalho normal; esta skill cuida só da forma).
2. Monte um JSON de blocos (formato abaixo) e salve em arquivo temporário.
   **Veio de mapa? Antes de montar o JSON**, confirme que nenhum item 🔴, ⏰,
   🟡, `[PESQUISA NÃO REALIZADA]` ou `[CONTRÁRIO NÃO RESOLVIDO]` ficou sem
   decisão do advogado — a lista completa está na seção acima.
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
   `qlmanage -t -s 1400 -o <dir> arquivo.pdf`) antes de entregar. **Se a
   peça tem `titulo` "Resumo" + `caixa_destaque` na página 1, essa
   checagem é obrigatória, não opcional** — confirme especificamente que
   a caixa aparece inteira na página 1 (extraia o texto da página com
   PyMuPDF e procure o título da caixa); a estimativa de linhas na hora
   de escrever o resumo é só um chute, não garante nada sozinha — ver
   "Resumo + caixa de destaque" em "Convenções da casa".

Salve o arquivo na pasta que o usuário indicar (ou na pasta do caso), com
nome no padrão **`<Tipo de Peça> - <Cliente>.docx`** — o tipo da peça vem
primeiro, depois o nome do cliente. Exemplos: `Petição Inicial -
Fulano.docx`, `Apelação - Beltrano.docx`, `Embargos Declaratórios -
Ciclano.docx`, `Agravo de Instrumento - Sicrano.pdf`. Use o tipo de peça
por extenso e legível (não abreviado), e o primeiro nome (ou nome usual)
do cliente, como o usuário já se refere a ele na conversa.

## Quando vem de um mapa de caso

Se a skill `mapa-de-caso` rodou antes (mapa salvo na pasta do caso ou montado
na conversa), ele é a fonte do conteúdo — não reescreva do zero:

- **Dos Fatos** sai da cronologia do mapa, na ordem das datas, cada fato com a
  prova citada por arquivo e folhas.
- **Do Direito** sai da matriz de amarração: um bloco por pedido, subindo tese
  → fato → prova → precedente verificado — a citação é a **ficha de
  precedente** inteira (ver "Citações verificadas" abaixo), não um resumo
  solto. Precedente que o mapa marcou como "aplica por extensão" entra na
  peça dizendo que é extensão, em parágrafo próprio, fora das aspas — não
  como se a ratio batesse direto.
- **Pedidos** saem dos nós `PD`, na ordem de dependência lógica.

**PARE antes de gerar se o mapa deixou qualquer coisa para resolver antes do
protocolo** — não só o que está marcado 🔴, mas também prazo e preclusão (⏰),
tese em 🟡 que dependa de decisão sua, precedente com `[PESQUISA NÃO
REALIZADA]` (a pesquisa não rodou — não é "não localizado"),
`[CONTRÁRIO NÃO RESOLVIDO]` (precedente adverso que ninguém leu até o fim), e
`PR` que o mapa marcou "distingue" de um fato do caso (o precedente não
sustenta a tese como está — citá-lo assim é o erro que a parte contrária
desmonta em uma linha). Diga quais são, explique o que cada uma muda no
documento, e pergunte antes de montar o JSON. Não é formalidade: uma
reconvenção que precluiu, ou uma peça que alega vício oculto e avaria
aparente ao mesmo tempo, custa o caso — e o DOCX timbrado sai igualmente
bonito nos dois casos.

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
lembrada de memória — e lembre que o lint de citações (seção "Citações
verificadas" abaixo) confere a peça contra a ficha no build, mas quem escreve
a ficha é o `pesquisador-juridico`; este portão aqui é anterior a isso, e
existe para nem chegar a montar o JSON com pendência sem decisão do advogado.

## Formato do JSON

```json
{
  "output": "/caminho/Tipo de Peca - Cliente.docx",
  "blocks": [
    {"tipo": "enderecamento", "texto": "Ao Juízo Cível da Comarca de Porto Velho/RO"},
    {"tipo": "processo", "texto": "Processo nº 0000000-00.0000.0.00.0000"},
    {"tipo": "espaco"},
    {"tipo": "paragrafo", "texto": "**NOME DA PARTE**, nacionalidade, estado civil, profissão, RG, CPF, endereço, por intermédio do advogado que esta subscreve, vem apresentar **CONTESTAÇÃO**, pelas razões a seguir."},
    {"tipo": "titulo", "texto": "I. Síntese da demanda"},
    {"tipo": "paragrafo", "texto": "Texto justificado; use **negrito**, *itálico* e __sublinhado__ inline."},
    {"tipo": "caixa_destaque",
     "titulo": "RAZÕES PARA CONCESSÃO DA LIMINAR",
     "itens": ["Primeiro ponto, curto e direto.", "Segundo ponto.", "Terceiro ponto."]},
    {"tipo": "subtitulo", "texto": "II.1. Da preliminar tal"},
    {"tipo": "citacao", "texto": "Citação longa de ementa/doutrina/decisão — recuo de 1cm, fonte 10,5pt, entre aspas, sem itálico."},
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
- `enderecamento` — 12pt negrito. Sempre em Title Case, sem a fórmula
  "EXCELENTÍSSIMO(A) SENHOR(A) DOUTOR(A) JUIZ(A) DE DIREITO..." e sem
  caixa-alta (regra do usuário, ago/2026 — ele não quer essa formalidade;
  o CPC, art. 319, I, só exige identificar o juízo a que a peça é
  dirigida, não esse formulário). Para 1ª instância: "Ao Juízo Cível da
  Comarca de Porto Velho/RO" (troque "Cível" pela vara/especialização
  certa quando o usuário indicar uma, ex. "Ao Juízo da Vara de Família
  da Comarca de..."). Para agravo de instrumento (o único recurso
  interposto direto no tribunal, sem passar pelo juízo a quo): "Ao
  Egrégio Tribunal de Justiça de Rondônia". **Para apelação, recurso
  especial e agravo em recurso especial, isso NÃO se aplica —** esses
  recursos precisam de DOIS endereçamentos (petição de interposição +
  razões, endereços diferentes cada um) — ver "Recursos direcionados a
  outro órgão" abaixo, não use só "Ao Egrégio Tribunal..." direto para
  eles. Para agravo interno: dirigido ao **relator**, não ao tribunal em
  geral — "Ao Eminente Relator, Desembargador(a) [nome]" (ou "Ao
  Relator" se o nome não for informado) — é um recurso decidido pelo
  mesmo órgão que proferiu a decisão monocrática, não uma petição de
  interposição para outro órgão.
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
- `citacao` — citação longa de ementa/doutrina/decisão, em parágrafo
  dedicado, recuo de **1cm**, **10,5pt**, **entre aspas**, **sem itálico**
  (regra do usuário, ago/2026 — recuo + parágrafo próprio já marcam a
  transcrição, o itálico é redundante aqui. O bloco aplica as aspas automaticamente
  ao redor de `"texto"` se ele não vier com elas; não precisa marcar
  `*asteriscos*` no texto, isso é só para a citação curta dentro de
  `paragrafo`, ver abaixo — essa continua em itálico, não mudou).
  Aceita `"atribuicao"` opcional — a referência ao final ("(Parecer nº
  10.452/2026, id. 36004312, 29/07/2026)", "(STJ, REsp .../SP, Rel. Min.
  Fulano, j. .../.../....)") — que fica **fora das aspas**, depois
  delas: não é texto citado, é referência bibliográfica. **Nunca
  concatene a atribuição dentro de `"texto"`**: o auto-quote colocaria
  aspas em volta dela também, o que é errado — a atribuição não faz
  parte da transcrição. **Transcrição de artigo de lei/código não leva
  campo próprio** — não prefixe "CPC, Art. 1º" dentro de `"texto"`.
  Identifique a norma num `paragrafo` ANTES do bloco `citacao` ("Dispõe o
  art. 1º do CPC:") e deixe `"texto"` só com a transcrição literal do
  dispositivo. Use para citação longa (mais de ~2-3 linhas): reproduza o
  trecho na íntegra, não como aspas dentro de um `paragrafo` comum. **Se
  suprimir
  trecho da transcrição, use colchetes `[...]`, nunca parênteses
  `(...)`** — vale em qualquer citação, curta ou longa. Ver regra
  completa em "Citação de julgado/doutrina" abaixo.
- `caixa_destaque` — **quadro de destaque** (o elemento "tipografado" das
  peças do escritório): faixa azul-marinho à esquerda com `titulo` em
  branco + lista de `itens` (marcadores) na área cinza. Use para os
  pontos-chave da liminar/tutela ou uma síntese em bullets. Cada item
  aceita marcação inline. **Sempre seguido por um bloco com espaçamento
  "before" próprio** (tipicamente `titulo`), nunca por um `paragrafo`
  colado direto — o bloco não emite mais um parágrafo em branco depois
  de si (removido em set/2026: quando a caixa cabia no fim da página,
  esse vazio sobrava sozinho no topo da página seguinte, criando um vão
  visível; o respiro agora vem do "before" do bloco seguinte).
  **NUNCA coloque `quebra_pagina` logo depois de `caixa_destaque`**
  (achado real, set/2026, reproduzido 2x de forma idêntica): gera uma
  página inteira em branco entre a caixa e o conteúdo seguinte — não é
  flutuação de hifenização, é determinístico com esse par de blocos.
  Causa provável: `quebra_pagina` é um parágrafo vazio "colado direto"
  (viola a regra acima) logo após uma tabela, e o parágrafo mínimo que
  todo `<w:tbl>` exige logo em seguida (exigência do próprio schema
  OOXML) some com o `<w:br w:type="page"/>` do meio. **Se o pedido for
  "a página deve terminar com a caixa"**: NÃO force quebra de página.
  Em vez disso, empurre o BLOCO INTEIRO resumo+caixa para perto do
  rodapé com `espaco` **antes do título "Resumo"** (não entre o resumo e
  a caixa — o resumo e a caixa ficam colados um no outro, como em
  qualquer peça normal; achado do usuário, mesma sessão: a 1ª tentativa
  pôs os `espaco` entre o 2º parágrafo do resumo e a caixa, o que deixou
  um vão feio bem ali no meio — "o vão deve ficar entre o resumo e os
  dados acima", ou seja, entre o bloco apelante/apelado/`processo` e o
  título "Resumo da Apelação"). Cada `espaco` ≈ 24-27pt; comece com 4-5 e
  confira a posição renderizada — ver `references/formatacao.md` se
  precisar da conta exata — até sobrar só ~50-100pt de caixa até o
  rodapé; a paginação natural do Word/LibreOffice então empurra sozinha o
  próximo `titulo` para a página seguinte, sem quebra manual e sem página
  em branco. Testado e
  confirmado: com a caixa terminando a ~50pt do rodapé, o título
  seguinte migra sozinho, de forma limpa, para a página seguinte.
- `pedido` — item de pedido com `marcador` em **negrito** e recuo
  deslocado (as linhas seguintes alinham sob o texto). `nivel: 2` recua
  mais (para subitens tipo `a.1)`, `a.2)`, `a.3)`). Prefira este bloco a
  parágrafos "a) ..." soltos — é o padrão visual das peças recentes.
  **`texto` sempre começa com letra maiúscula** — aplicado
  automaticamente pelo script (`cap_primeira_letra`, regra do usuário,
  set/2026), não precisa capitalizar na mão ao escrever o JSON, mas
  escreva como se fosse maiúsculo mesmo assim (mais legível no JSON).
  **Sempre que um pedido se desdobrar em subpedidos ou tiver pedido
  subsidiário/alternativo, abra os subitens com `nivel: 2`** (marcador
  `a.1)`, `a.2)`, `a.3)` — letra minúscula do pedido-pai + número —, não
  amontoe tudo num parágrafo só nem deixe o pedido subsidiário
  disfarçado dentro do texto do pedido principal. Ver "Conteúdo dos
  pedidos" abaixo para o que entra no `texto` de cada um.
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
  colunas (7+) ficam apertadas em fonte padrão (10,5pt) — colunas muito
  estreitas ainda podem forçar quebra feia mesmo com hifenização
  automática ligada (ver "Hifenização automática" abaixo). Para 7+ colunas, sempre:
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
  **Segundo signatário (co-advogado):** passe `"nome2"`/`"oab2"` para
  incluir um co-advogado assinando junto (ex.: `"nome2": "Fulano de
  Tal", "oab2": "OAB/RO 00000"`). Ele aparece centralizado
  na metade esquerda do fecho, ao lado do nome/OAB principal (que fica na
  direita, sob a assinatura manuscrita) — a célula esquerda existe vazia
  por padrão justamente para isso. Sem assinatura manuscrita própria (a
  skill só tem a imagem da assinatura do Roberto embutida); a assinatura
  eletrônica real do co-advogado vem de quem protocola no PJe, não do
  DOCX. Adicionado ago/2026.

## Convenções da casa (extraídas das peças reais)

- **Siglas, não nome por extenso** (regra do usuário, ago/2026): no corpo
  do texto, use a sigla do tribunal/norma, não o nome por extenso — "STJ"
  (não "Superior Tribunal de Justiça"), "TJRO" (não "Tribunal de Justiça
  de Rondônia" ou "Tribunal de Justiça do Estado de Rondônia"), "CPC"
  (não "Código de Processo Civil"), e o mesmo padrão para qualquer outra
  sigla consagrada: STF, STJ, TJRO, CPC, CC, CDC, CLT, CF, art., §, inc.
  Vale para `paragrafo`, `citacao` (fora da transcrição literal — a
  transcrição em si reproduz o texto original, sigla ou não, como está
  na fonte), `subtitulo`, `titulo`, `pedido`, `caixa_destaque` — qualquer
  corpo de texto autoral. **Exceção**: o `enderecamento` (saudação formal
  ao juízo/tribunal) continua por extenso — "Ao Egrégio Tribunal de
  Justiça de Rondônia", não "Ao Egrégio TJRO" — é a fórmula de abertura
  da peça, gênero textual diferente de citação no corpo.
- Endereçamento (12pt negrito): sempre em Title Case, para qualquer
  instância, sem a fórmula "EXCELENTÍSSIMO(A) SENHOR(A) DOUTOR(A) JUIZ(A)
  DE DIREITO..." e sem caixa-alta (regra do usuário, ago/2026 — ver
  detalhe no tipo de bloco `enderecamento` acima). 1ª instância: "Ao
  Juízo Cível da Comarca de Porto Velho/RO" (ou a vara/especialização
  certa, se indicada). Tribunal: "Ao Egrégio Tribunal de Justiça de
  Rondônia". Vai direto ao `Processo nº` (itálico) e um `espaco` antes
  da qualificação.
- Nome das partes em **negrito** na primeira menção, sempre em Title Case
  ("Roberto Grécia Bessa", nunca "ROBERTO GRÉCIA BESSA") — mesmo em 1ª
  instância; nunca caixa-alta total, mesmo que o enderecamento acima esteja
  em caixa-alta (regra do usuário, ago/2026 — isso não muda entre 1ª
  instância e recurso, é sempre Title Case).
- Nome da peça (CONTESTAÇÃO, EXECUÇÃO DE TÍTULO EXECUTIVO EXTRAJUDICIAL...)
  em negrito, em caixa-alta, dentro do MESMO parágrafo da qualificação das
  partes — nunca como título nem como parágrafo à parte (regra do usuário,
  ago/2026). Um único `paragrafo` flui do começo ao fim: "**Fulano de Tal**,
  qualificação completa..., vem propor a presente **AÇÃO TAL**... em face
  de **Beltrano de Tal**, qualificação completa..., pelos fatos e
  fundamentos a seguir expostos." Não separe a qualificação, o nome da
  peça e o "em face de" em blocos `paragrafo` distintos.
- Seções numeradas no próprio texto do título: `I. Resumo`, `II. ...`;
  subseções como subtítulo: `II.1. Da...`.
- Estrutura típica: Resumo/Síntese → fundamentos por seção → Pedidos.
- **Pedidos**: use o bloco `pedido` (marcador em negrito + recuo deslocado),
  não parágrafos "a) ..." soltos. Marcadores no padrão das peças: `A.`,
  `B.`, `C.`... com subitens `a.1)`, `a.2)`, `a.3)` (`nivel: 2`).
- **Primeira letra do pedido sempre maiúscula, e subpedido/pedido
  subsidiário sempre em `nivel: 2`** (regra do usuário, set/2026): o
  `texto` de cada `pedido` começa com maiúscula — o script já corrige
  isso sozinho (`cap_primeira_letra`), então não é preciso decorar, mas
  escreva assim de qualquer forma. E sempre que um pedido tiver
  desdobramento (vários subpedidos) ou pedido subsidiário/alternativo
  ("caso não seja esse o entendimento, subsidiariamente..."), abra
  esses subitens como pedidos `nivel: 2` próprios (`a.1)`, `a.2)`,
  `a.3)` — letra minúscula do pedido-pai + número — em vez de embutir
  tudo dentro do texto corrido do pedido principal. Exemplo:
  ```json
  {"tipo": "pedido", "marcador": "A.", "texto": "A reforma da sentença para julgar procedente o pedido de indenização, com os seguintes desdobramentos:"},
  {"tipo": "pedido", "marcador": "a.1)", "nivel": 2, "texto": "condenação ao pagamento de R$ 10.000,00 a título de danos morais;"},
  {"tipo": "pedido", "marcador": "a.2)", "nivel": 2, "texto": "condenação ao pagamento das custas e honorários sucumbenciais;"},
  {"tipo": "pedido", "marcador": "B.", "texto": "Subsidiariamente, caso não seja este o entendimento, a anulação da sentença para novo julgamento."}
  ```
  (repare que `a.1)`/`a.2)` também começam com minúscula — só o
  marcador nivel 1 usa letra maiúscula, `A.`/`B.`/`C.`; o `texto` de
  cada subitem, esse sim, começa maiúsculo, aplicado automaticamente).
- **Conteúdo dos pedidos — completo, mas sem fundamentação** (regra do
  usuário, ago/2026): o juiz pode ler só os pedidos e ignorar a
  fundamentação — por isso cada pedido tem que dizer, sozinho, exatamente
  o que se quer. Duas armadilhas opostas a evitar:
  - **Não remeta à fundamentação** — nunca escreva um pedido vago que só
    aponta de volta pro corpo da peça: "seja julgado procedente o
    pedido", "nos termos acima expostos", "conforme fundamentado", "pelos
    motivos já expostos". Se o juiz não ler a fundamentação, um pedido
    assim não diz nada. Escreva o objeto do pedido por extenso, mesmo que
    isso repita informação já dada nas seções anteriores — pedido tem que
    ser autossuficiente.
  - **Mas também não fundamente dentro do pedido** — não é pra colar o
    "porquê" ali. Um pedido não é "seja declarada a nulidade da citação,
    visto que o espólio não foi regularmente citado nos termos do art.
    75, VII, do CPC e o AR foi recebido por pessoa estranha aos autos"
    (isso é fundamentação, pertence à seção de mérito). É "seja declarada
    a nulidade da citação do espólio realizada por meio do AR juntado ao
    id. 123456789, determinando-se nova citação na pessoa do
    inventariante" — assertivo, objetivo, diz o quê e (quando aplicável)
    em quem/como, sem o "porque".
  - Cada pedido nomeia o objeto concreto: a decisão/ato que se quer ver
    reformado, mantido, declarado, concedido ou determinado — com id.,
    valor, prazo ou parte específica quando existirem, não uma referência
    genérica ("o pedido", "a pretensão", "o quanto requerido").
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

  **A estimativa de linhas é só um chute inicial, NÃO uma garantia —
  confira sempre, é obrigatório, não opcional** (achado real, ago/2026):
  peça gerada com exatamente 3 parágrafos curtos de resumo, dentro do
  orçamento de linhas acima, ficou bem na borda — o MESMO documento
  (texto idêntico), convertido pra PDF em dois momentos diferentes, uma
  vez deixou a caixa inteira na página 2 (página 1 com um vão em branco
  enorme no fim) e outra vez coube certinho na página 1. A diferença não
  foi o texto — foi o quanto a hifenização automática comprimiu as
  linhas naquele render específico (ver "Hifenização automática" em
  "Regras importantes"): mais pontos de hífen = linhas mais cheias =
  menos linhas no total = mais chance de caber. Isso significa que
  **o mesmo resumo pode passar num ambiente e falhar em outro**
  (LibreOffice com dicionário completo vs. sem dicionário vs. Word vs. o
  Cowork, que não tem nenhum dos dois — hifenização zero lá, o pior
  caso). Por isso:
  1. Depois de gerar o PDF, **sempre** confira especificamente se a
     caixa de destaque aparece inteira na página 1 — não vale só abrir o
     PDF e "olhar se parece bem"; extraia o texto da página 1 (ex.
     PyMuPDF: `page.get_text()`) e confirme que o título da caixa
     ("RAZÕES PARA...") está lá.
  2. Se não estiver (ou se sobrar um vão em branco grande no fim da
     página 1 em vez da caixa), corte uma frase do resumo — não da caixa
     — e gere de novo. Repita até confirmar.
  3. Não presuma que "seguiu a regra das 3 linhas/30-35 por página,
     então está garantido" — a regra é o ponto de partida, a checagem é
     o que garante. Isso vale mesmo se o resumo já pareceu curto o
     bastante da primeira vez.

  **A página 1 termina com a caixa; o primeiro tópico abre a página 2**
  (regra do usuário, 10/09/2026, padrão para toda peça com resumo +
  caixa). Nada do corpo da peça ("I. Dos fatos" ou equivalente) pode
  começar na página 1 abaixo da caixa. Técnica: empurre o bloco
  resumo + caixa para baixo com blocos `{"tipo": "espaco"}` **antes do
  título "Resumo"** (nunca entre o resumo e a caixa, nunca
  `quebra_pagina` depois da caixa, que gera página em branco), até o
  título da primeira seção migrar sozinho para a página 2. Comece com
  3 `espaco` e confira com o verificador, que diz o que ajustar:
  ```bash
  python3 <skill>/scripts/check_pagina1.py "Peca.pdf"   # opções: --caixa "RAZÕES PARA" --secao "I."
  ```
  Ele falha se o tópico ficou na página 1 (acrescente um `espaco`), se a
  caixa saiu da página 1 (retire um `espaco` ou corte uma frase do
  resumo) ou se a página 2 não começa pelo tópico. Rode sempre, depois
  de cada conversão para PDF: a hifenização muda de um render para
  outro, e o mesmo texto pode passar num e falhar noutro. Caso real
  (arguição de impedimento, 10/09/2026): 3 `espaco` bastaram; a caixa
  terminou a ~100pt do rodapé e o título foi sozinho para a página 2.
- **Recursos direcionados a outro órgão: interposição + razões, duas
  peças, dois endereçamentos** (regra do usuário, set/2026, pesquisada
  na web antes de implementar — ver fontes ao final). Vale para
  **apelação, recurso especial e agravo em recurso especial (art.
  1.042 CPC)** — não para agravo de instrumento (já vai direto ao
  tribunal, sem juízo a quo no meio) nem para agravo interno (decidido
  pelo mesmo órgão que proferiu a decisão monocrática, petição única
  dirigida ao relator).
  - **Por quê**: esses três recursos são apresentados perante uma
    autoridade (o juízo que proferiu a sentença, ou o(a)
    Presidente/Vice-Presidente do tribunal recorrido) que não é quem
    vai julgar o mérito do recurso — julgar é o tribunal ad quem
    (apelação) ou o STJ (recurso especial e agravo em recurso especial).
    Por isso a peça se divide em duas partes com endereçamentos
    diferentes: uma **petição de interposição**, curta, sem
    fundamentação de mérito, dirigida a quem vai RECEBER e PROCESSAR o
    recurso; e as **razões recursais**, com toda a fundamentação,
    dirigidas a quem vai JULGAR.
  - **Estrutura em blocos** (um único DOCX, as duas partes seguidas):
    ```json
    {"tipo": "enderecamento", "texto": "Ao Juízo Cível da Comarca de Porto Velho/RO"},
    {"tipo": "processo", "texto": "Processo nº ..."},
    {"tipo": "espaco"},
    {"tipo": "paragrafo", "texto": "**Fulano de Tal**, já qualificado(a) nos autos, por seu advogado que esta subscreve, não se conformando com a r. sentença de id. ..., vem, respeitosamente, interpor o presente RECURSO DE APELAÇÃO, pelas razões anexas, requerendo:"},
    {"tipo": "paragrafo", "texto": "A gratuidade da justiça foi deferida à parte recorrente na decisão de id. ... e mantida expressamente na sentença ora recorrida (id. ...), o que dispensa o preparo do presente recurso, nos termos do art. 98 do CPC."},
    {"tipo": "pedido", "marcador": "A.", "texto": "o recebimento e o regular processamento do presente recurso;"},
    {"tipo": "pedido", "marcador": "B.", "texto": "a intimação da parte apelada para oferecer contrarrazões no prazo legal;"},
    {"tipo": "pedido", "marcador": "C.", "texto": "a posterior remessa dos autos ao Egrégio Tribunal de Justiça de Rondônia, para julgamento do recurso."},
    {"tipo": "fecho", "recurso": false, "data": "...", "nome": "...", "oab": "...", "assinatura": true},
    {"tipo": "quebra_pagina"},
    {"tipo": "titulo", "texto": "Razões de Apelação", "centralizado": true},
    {"tipo": "paragrafo", "texto": "Apelante: **Fulano de Tal**"},
    {"tipo": "paragrafo", "texto": "Apelado: **Beltrano de Tal**"},
    {"tipo": "paragrafo", "texto": "Processo nº ..."},
    ... resumo (se peça longa) + corpo + pedidos como qualquer peça ...,
    {"tipo": "fecho", "recurso": true, "data": "...", "nome": "...", "oab": "...", "assinatura": true}
    ```
    **Se houve gratuidade da justiça deferida no processo, a
    interposição diz isso e cita o id. da decisão que deferiu (e da
    sentença/decisão recorrida, se ela também a manteve), para dispensar
    o preparo (art. 98, CPC)** — regra do usuário, set/2026: "deve
    indicar se houve concessão de justiça gratuita e indicar o id.,
    assim, dispensando o preparo". Sem gratuidade no processo, omita
    esse parágrafo (não afirme dispensa de preparo sem base real nos
    autos) — confirme com o usuário ou releia a sentença antes de supor.
    **A petição de interposição LEVA `fecho`/assinatura própria** (regra
    corrigida em set/2026 — a 1ª versão desta regra dizia o contrário e
    o usuário rejeitou o resultado: "ficou horrível... falta assinatura,
    minha oab" — uma petição dirigida ao juízo, mesmo curta e sem
    mérito, é um ato processual que se assina, não um anexo). Ambas as
    partes fecham com seu próprio `fecho` completo (data + assinatura +
    nome + OAB) — assinar duas vezes no mesmo documento **é** a praxe
    aqui, porque são duas petições dirigidas a autoridades diferentes.
    Só o **texto do encerramento** difere: a interposição usa
    `"recurso": false` → "Nestes termos, pede deferimento." (é um
    requerimento ao juízo a quo, não um julgamento de mérito); só o
    `fecho` final das razões usa `"recurso": true` → "pede provimento".
    Escreva o corpo da interposição como pedidos (`tipo: "pedido"`, não
    um parágrafo corrido) — recebimento, intimação da apelada para
    contrarrazões, remessa ao tribunal — pelo mesmo motivo que qualquer
    outra peça usa blocos `pedido`: mais claro para quem lê rápido.
    **O título "Razões de Apelação"/"Razões de Recurso Especial" leva
    `"centralizado": true`** (regra do usuário, set/2026): é um título de
    capa da segunda parte do documento, não um título de seção numerada
    (`titulo` já sai em 14pt por padrão — não precisa de ajuste de
    tamanho, só o alinhamento central).
    **As razões NÃO repetem `enderecamento`** (regra do usuário, mesma
    sessão, corrigida depois de ver o resultado real: "após as razões da
    apelação, apague 'Ao Egrégio Tribunal...'") — o título centralizado
    já nomeia a peça e a instância fica implícita; repetir "Ao Egrégio
    Tribunal de Justiça de Rondônia" logo abaixo do título é redundante.
    As razões vão direto do título para `Apelante:`/`Apelado:`/
    `Processo nº`.
  - **Endereçamento de cada parte**: só a petição de interposição leva
    `enderecamento` de verdade (as razões não repetem, ver acima):
    - Apelação: interposição → juízo de 1ª instância (mesmo padrão de
      `enderecamento` para 1ª instância).
    - Recurso especial / agravo em recurso especial: interposição → "Ao
      Presidente do Egrégio Tribunal de Justiça de Rondônia" (ou
      Vice-Presidente, conforme o caso — art. 1.029, CPC: dirigido a
      quem preside o tribunal recorrido).
  - **Resumo + `caixa_destaque` vão nas RAZÕES, nunca na
    interposição** (regra do usuário, set/2026): a interposição é
    puramente procedimental, sem mérito — o padrão de resumo (título com
    `linha` + 3 parágrafos + `caixa_destaque`, quando a peça for longa)
    entra logo depois do endereçamento/qualificação das razões, no
    mesmo lugar que entraria numa peça sem esse split.
  - **A petição de interposição não "pede provimento"** — ela não pede
    nada de mérito, só que o recurso seja recebido e processado. Só o
    `fecho` final das razões usa `"recurso": true` → "pede provimento".
    Não confundir os dois momentos.
  - Fontes consultadas (set/2026): [Trilhante — Apelação](https://trilhante.com.br/curso/recursos/aula/apelacao-4),
    [Modelo de apelação — Advbox](https://advbox.com.br/blog/modelos/apelacao-civel/),
    [Recurso especial — Aurum](https://www.aurum.com.br/blog/recurso-especial/),
    [Agravo interno — Aurum](https://www.aurum.com.br/blog/agravo-interno/),
    [Art. 1.042 CPC — Migalhas](https://www.migalhas.com.br/coluna/jurisprudencia-do-cpc/433065/art-1-042-do-cpc--agravo-em-recursos-especial-extraordinario).
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
    recurso extraordinário, embargos infringentes. **Apelação, recurso
    especial e agravo em recurso especial usam esse `"recurso": true`
    só no `fecho` FINAL das razões** — não na petição de interposição,
    que não tem `fecho` próprio (ver "Recursos direcionados a outro
    órgão" acima).
  - **Não é recurso** (→ `"recurso": false`, "pede deferimento"):
    petição inicial, contestação, réplica, cumprimento de sentença,
    impugnação ao cumprimento de sentença, embargos de declaração
    (é tecnicamente um recurso, mas na praxe da casa fecha como as
    demais petições — "pede deferimento" ou "pede acolhimento"),
    requerimento, manifestação.
  - Na dúvida sobre um tipo de peça não listado aqui, pergunte ao
    usuário antes de gerar — não adivinhe.
- **Citação de julgado, ementa, decisão ou doutrina** (regra do usuário,
  ago/2026, corrigida três vezes no mesmo mês: exigia itálico também na
  citação longa; foi corrigida para SEM itálico; o usuário corrigiu de
  novo para itálico; e por fim corrigiu uma 3ª vez, "não deixe em itálico
  o que é citação direta com recuo e parágrafo próprio" — vale esta
  última: **a citação com recuo e parágrafo próprio (bloco `citacao`)
  NÃO leva itálico; a citação curta/inline dentro de um `paragrafo`
  continua em itálico**, essa parte nunca mudou):
  - **Limite objetivo, curta x longa: 3 linhas** (regra do usuário,
    set/2026, substitui o "~2-3 linhas" anterior por um corte único e
    verificável). Antes de decidir o bloco, veja quantas linhas o trecho
    ocuparia no corpo da peça (11pt, largura normal de página) — abaixo
    de 3 linhas é curta; 3 linhas ou mais é longa, some para o bloco
    `citacao`, mesmo que o trecho "pareça" caber numa frase.
  - **Citação curta** (menos de 3 linhas, cabe dentro da frase corrente,
    entre aspas, sem virar parágrafo à parte): fica dentro do `paragrafo`
    normal, envolvendo só o trecho citado em `*asteriscos*` para sair em
    **itálico** — ex.: `"...conforme entendimento do STJ, *"a mora do
    devedor não se presume, deve ser comprovada"* (REsp 1.234.567/SP)."`
    A referência ao julgado/obra (tribunal, número, relator, página) fica
    fora dos asteriscos, em texto normal, sem itálico. **Nunca envolva a
    citação curta em `**negrito**`** — negrito é para termo/palavra-chave
    isolada dentro do próprio texto autoral, itálico é o marcador de
    transcrição alheia; misturar os dois deixa a peça com negrito em
    excesso e a citação difícil de distinguir do que o advogado escreveu.
  - **Citação longa** (3 linhas ou mais, ementa, doutrina ou decisão
    transcrita em parágrafo dedicado — "quando você dedica um parágrafo"
    nas palavras do usuário): use o bloco `citacao` — **entre aspas**, **sem itálico**,
    **10,5pt** (era 10pt, ajustado a pedido do usuário — ago/2026)
    (o bloco já aplica as aspas automaticamente ao redor de `"texto"` se
    ele não vier com elas) e **recuo de 1cm** (não é mais 2,5cm —
    reduzido a pedido do usuário). Reproduza o trecho integralmente em
    `"texto"`, sem marcar `*asteriscos*` manualmente — o recuo e o
    parágrafo dedicado já bastam para marcar a transcrição, o itálico
    ficava redundante. A atribuição (tribunal/juízo, número do julgado,
    relator, data — ou autor/obra/página para doutrina) vai no campo
    **`"atribuicao"`** separado, nunca dentro de `"texto"`: ela fica
    **fora das aspas**, no fim do mesmo parágrafo — não é texto citado,
    é referência bibliográfica — ex.: `"Ocorre que [...] esvazia o
    interesse recursal [...]." (Parecer nº 10.452/2026, id. 36004312,
    29/07/2026)`, onde só o trecho entre aspas é a transcrição e o
    `(Parecer nº...)` é a atribuição fora dela. **Nunca concatene a
    atribuição dentro de `"texto"`**: o auto-quote colocaria aspas em
    volta dela também, o que é errado.
  - Vale tanto para jurisprudência (ementa, acórdão, decisão monocrática)
    quanto para doutrina — a regra é a mesma para as duas, o que muda
    entre curta e longa é onde o texto fica (dentro da frase vs.
    parágrafo dedicado) **e** o itálico (curta leva, marcado pelo autor
    com `*asteriscos*`; longa não leva, nem precisa marcar nada).
  - **Dispositivo legal (artigo de lei/código) — sem referência dentro
    do bloco `citacao`, nem antes nem depois** (regra do usuário, ago/2026
    — revisada no mesmo dia: uma 1ª tentativa colocava "CPC, Art. 1º"
    dentro das aspas via campo `"dispositivo"`; o usuário corrigiu:
    "é melhor não colocar o CPC, seguido do dispositivo"). O padrão certo
    é: identifique a norma num **`paragrafo` normal ANTES** do bloco
    `citacao` — "Dispõe o art. 1º do Código de Processo Civil:" — e deixe
    `"texto"` do bloco `citacao` só com a **transcrição literal**, sem
    prefixo nenhum. Exemplo completo:
    ```json
    {"tipo": "paragrafo", "texto": "Dispõe o art. 1º do CPC:"},
    {"tipo": "citacao", "texto": "O processo civil será ordenado, disciplinado e interpretado conforme os valores e as normas fundamentais estabelecidos na Constituição da República Federativa do Brasil, observando-se as disposições deste Código."}
    ```
    Mesmo padrão de duas peças (parágrafo introdutório + `citacao`) já
    usado para ementa/decisão/doutrina — a única diferença de fato entre
    dispositivo legal e jurisprudência é que **dispositivo legal não usa
    `"atribuicao"`** (a referência já ficou inteira no parágrafo anterior,
    não faz sentido repeti-la dentro do bloco).
  - **Supressão de trecho: sempre colchetes `[...]`, nunca parênteses
    `(...)`** (regra do usuário, ago/2026) — vale em qualquer citação,
    curta ou longa, dispositivo legal, ementa, decisão ou doutrina. Ex.:
    `"[...] esvazia o interesse recursal [...]."`, nunca `"(...) esvazia
    o interesse recursal (...)."`.
  - **Negrito estratégico dentro de citação longa** (regra do usuário,
    set/2026): o bloco `citacao` aceita `**negrito**` no meio do texto
    entre aspas para destacar o trecho decisivo da transcrição — com
    sobriedade (uma frase ou cláusula curta por citação, nunca o
    parágrafo inteiro) e estratégia (o trecho que sustenta diretamente o
    argumento que vem antes ou depois da citação, não qualquer frase
    "importante" em abstrato). **Sempre que usar esse negrito, acrescente
    `", grifamos"` ao final do campo `"atribuicao"`** (antes do
    parêntese de fechamento) — é a prática padrão para avisar que o
    destaque não está no original. Sem negrito na citação, não acrescente
    "grifamos". O `runs()` do `build_docx.py` faz o split de `**...**` e
    `*...*` por regex simples, sem suporte a aninhamento: nunca coloque
    um `*itálico*` (termo em latim/língua estrangeira, ver regra abaixo)
    dentro de um trecho já em `**negrito**` — a sequência `**texto
    *interno* texto**` sai com asteriscos literais visíveis no PDF. Se o
    termo em itálico cair dentro do trecho que seria negritado, ajuste o
    corte do negrito para não sobrepor (ex.: encerre o `**negrito**` antes
    do termo, deixe o termo só em `*itálico*`, e retome outro `**negrito**`
    depois se necessário).
  - **Termos em latim ou em língua estrangeira: sempre em itálico**
    (regra do usuário, set/2026) — em qualquer bloco de texto autoral
    (`paragrafo`, `subtitulo`, `titulo`, `pedido`, `caixa_destaque`) e
    também dentro de bloco `citacao` (a transcrição preserva as palavras,
    mas a tipografia em itálico para estrangeirismo é convenção editorial
    de quem transcreve, não altera o conteúdo — por isso não exige
    "grifamos"). Ex.: `*custos vulnerabilis*`, `*in re ipsa*`, `*tempus
    regit actum*`, `*data venia*`, `*ab initio*`, `*decisum*`, `*pas de
    nullité sans grief*`. Vale para a primeira ocorrência e para todas as
    seguintes no mesmo documento (não é "só na primeira menção" como
    outras convenções da casa) — cada aparição do termo leva itálico,
    porque a marca é ortográfica, não uma explicação que já foi dada.
    Expressão já aportuguesada e de uso corrente em português jurídico
    (ex.: "habeas corpus" quando vira substantivo comum do texto, "per
    si", "a priori" só quando resta como locução emprestada) segue a
    mesma regra: se ainda soa como estrangeirismo, vai em itálico. Termos
    consagrados que já viraram siglas ou nomes próprios de instituto
    (ex.: "STJ", "CPC") não entram nessa regra.
- **A cidade do fecho é SEMPRE Porto Velho/RO**, porque é onde fica o
  escritório e onde o advogado assina — independentemente de onde tramita
  o processo. Um agravo endereçado ao Tribunal de Justiça de outro
  estado, ou uma peça numa comarca como Fernandópolis/SP, ainda assim
  fecha com "Porto Velho/RO, {data}", nunca com a cidade do processo.
  Por isso passe só `"data"` no bloco `fecho` (não `"cidade_data"`) —
  a cidade já vem certa sozinha. Use `"cidade_data"` só se o usuário
  pedir expressamente uma cidade diferente.
- **Valor da causa ao final da peça — só em petição inicial ou
  reconvenção** (regra do usuário, ago/2026). Nunca inclua "Dá-se à causa
  o valor de R$..." em agravo de instrumento, agravo interno, apelação,
  recurso especial/extraordinário ou qualquer outro recurso — o valor da
  causa já foi fixado lá atrás, na inicial; o recurso não abre um novo
  valor, só impugna uma decisão dentro do processo que já tem o seu.
  Reconvenção é exceção porque, tecnicamente, abre uma nova demanda
  dentro do mesmo processo e por isso tem valor da causa próprio (art.
  292, CPC). Contestação, réplica, cumprimento de sentença, embargos de
  declaração e as demais peças também não levam essa declaração — só
  petição inicial e reconvenção.
- **Sem tópico de cabimento, tempestividade ou prequestionamento por
  padrão** (regra do usuário, jul/2026, reforçada set/2026 para cobrir
  contrarrazões). Nenhuma peça leva seção "Do cabimento", "Da
  tempestividade" ou "Do prequestionamento" a menos que o usuário peça
  expressamente. Vale também para **contrarrazões a embargos de
  declaração**: não abra com "Do cabimento das contrarrazões" citando o
  art. 1.023, §2º, do CPC — vá direto ao mérito da resposta. Prequestionamento
  só entra quando a peça tiver esse fim explícito (embargos de declaração
  para preparar REsp/RE, ou o próprio recurso excepcional).
- **Sem travessão** (regra do usuário, set/2026, valendo para qualquer
  peça e qualquer texto que a skill produza). Escreva com vírgula, ponto
  ou parênteses; travessão em excesso lê como texto gerado por IA. Rode
  a skill `humanizer` numa revisão final antes de entregar qualquer
  peça longa, sobretudo quando ela tiver muito texto argumentativo
  próprio (não apenas citação literal, onde o travessão do original é
  preservado).

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
  - **O `encerramento` precisa ficar CURTO e genérico — nunca escreva ali
    a prosa de fechamento específica do caso.** A assinatura manuscrita
    (`assets/sig_drawing.xml`) é uma imagem ancorada com deslocamento
    FIXO em EMU relativo ao parágrafo do encerramento (-408305 EMU ≈
    -32pt na vertical a partir do topo do parágrafo; ≈3,53" da margem
    esquerda na horizontal; ≈88pt de altura própria) — não escala com
    quanto texto o parágrafo ocupa. Dois incidentes reais, por lados
    opostos: (1) jul/2026 — encerramento de 1 linha só ("Estando de
    acordo, as partes assinam este termo em duas vias iguais.", 68
    caracteres) saiu **riscado pela assinatura**; (2) 28/08/2026 — um
    encerramento de 2 linhas AINDA colidiu, porque a 2ª linha se
    estendia até a coluna onde a imagem está ancorada horizontalmente
    (~3,53"). Ou seja, "precisa ocupar 2 linhas" não é a regra certa — o
    que importa é nenhuma linha alcançar aquela coluna, e isso depende do
    texto exato: não dá pra garantir só contando linha.
    **Regra atual: mantenha `encerramento` sempre uma frase curta e
    genérica** (~40-60 caracteres — ex.: "Fico à disposição para
    eventuais esclarecimentos.", ou "Atenciosamente," fora do padrão
    recurso/deferimento). **Se o caso pedir um fechamento mais específico
    ou longo, coloque-o num `paragrafo` normal ANTES do bloco `fecho`**,
    fora da zona de risco geométrica — o encerramento do fecho em si
    continua curto. Mesmo assim, sempre confira a página renderizada do
    fecho antes de entregar.
  - **Página de assinaturas**: ponha um `quebra_pagina` antes da última
    seção (a de aceite/quitação) para que ela e as duas assinaturas
    fiquem juntas numa página só. Sem isso, o bloco do cliente costuma
    cair sozinho na página seguinte, órfão da assinatura do advogado —
    ruim de ler e pior ainda no ZapSign.

## Citações verificadas (lint obrigatório)

O build (`build_docx.py`) roda `scripts/lint_citacoes.py` antes de gerar e
**recusa a peça** se encontrar citação de julgado sem ficha verificada ou
divergente da ficha. Motivo: em set/2026 uma peça citou o conteúdo de um
acórdão com o relator de OUTRA decisão do mesmo número (um número CNJ pode ter
três acórdãos: original, embargos, segundos embargos), descreveu data e
resultado errados de um precedente, parafraseou uma tese de repetitivo além do
que foi fixado, e uma peça já protocolada citava um REsp real com conteúdo que
não era dele. "Nunca cite de memória" deixou de ser disciplina e virou
propriedade do build.

O que o lint faz, por citação encontrada no texto (número CNJ, REsp/AREsp/
AgInt/RE/HC..., Tema, Súmula, IRDR, acórdão de Tribunal de Contas no formato
sigla+número — `APL-TC`, `AC1-TC`, `AC2-TC`, `APLR-TC`, `AC1R-TC`, `AC2R-TC`
seguido de `NNNNN/AA`, 14/09/2026, siglas reais do TCE-RO; sigla de outro TC/TCU
fora desse desenho não é reconhecida):

- **sem ficha** em `precedentes` → ERRO;
- **relator, data (dd/mm/aaaa) ou órgão** na frase/atribuição diferentes da
  ficha → ERRO;
- bloco `citacao`: o **texto entre aspas** é conferido, segmento a segmento
  (cortes marcados com `[...]`), contra `trecho`/`dispositivo`/`tese`/`ementa`
  da ficha → paráfrase ou corte sem `[...]` é ERRO;
- ficha `"só ementa/índice"` → AVISO; `"não conferido"` conta como sem ficha;
  ficha com `verificado_em` há mais de 180 dias → AVISO; ficha nunca citada → AVISO.
- precedente do **TJRO** citado como **"3ª Câmara Cível"** sem `"orgao_fonte": "fecho"`
  na ficha → ERRO. O cadastro do portal põe na 3ª acórdãos julgados pela 1ª ou
  pela 2ª (15 de 24 processos na medição de 14/09/2026), e a ficha que copia o
  cadastro passa limpa na conferência peça × ficha: foi assim em 4 peças reais.
  A câmara que vale é a do fecho do acórdão ("acordam os Magistrados da(o) ...").
- **link do inteiro teor** (pedido do usuário, 14/09/2026): todo julgado citado cuja
  ficha traga `link` de domínio público (`.jus.br`, `.tc.br`, `.gov.br`, `.leg.br`,
  `.mp.br`) sai com a **referência inteira clicável** — "(TJRO, Agravo de Instrumento
  NNNNNNN-NN.AAAA.8.22.0000, 1ª Câmara Cível, Rel. ..., j. .../.../....)", parênteses
  incluídos, não só o número — para o inteiro teor, no DOCX e no PDF (azul-marinho,
  sublinhado; o texto da peça não muda), para o juiz conferir a fonte. Refinado em
  14/09/2026 a pedido do usuário: a 1ª versão linkava só o número, "pouco visível
  dentro da referência". **Só a primeira menção de cada julgado/tema no documento
  vira link** (pedido do usuário, 15/09/2026: peça que cita "Tema 1300"/"Tema 1150"
  em várias frases saía com hiperlink em cada menção, poluindo o texto corrido) —
  `build_docx.py` guarda em `_LINKED_URLS` toda URL já usada e não linka de novo a
  mesma URL, mesmo que a citação reapareça em bloco diferente; as menções seguintes
  saem em texto normal, sem sublinhado nem cor de link. **Citação de classe "tema"
  (bare "Tema 1300"/"Tema 1150", sem número de REsp/acórdão junto) nunca vira link,
  nem na primeira menção** (refinamento do usuário, mesmo dia, 15/09/2026) —
  `_CLASSES_SEM_LINK = {"tema"}` em `build_docx.py`, `runs()` filtra `_LINKS`
  removendo todo ident cuja classe esteja nesse conjunto antes de chamar
  `segmentar_links`; a citação formal do julgado (REsp, número do acórdão, id.) que
  sustenta aquele tema continua linkável normalmente. `segmentar_links` expande para o grupo `(...)` que envolve a
  citação quando ela é a única linkável ali dentro (duas citações linkáveis no mesmo
  parêntese, ex. separadas por ";", não expandem — cada uma linka só o próprio número,
  para não apontar o mesmo trecho a dois lugares); fora de parênteses, linka só o
  número, como antes. Ficha sem `link` → AVISO, a peça sai sem link para aquele julgado
  — **nunca fabrique um link para não sair esse aviso**: no teste de demonstração desta
  mesma tarde, um `num_registro` inventado para uma ficha de exemplo caiu em página
  inexistente do STJ; link de demonstração segue a mesma regra do link real, só entra
  se for verificado. Link fora de portal oficial (JusRatio, Jusbrasil, blog) → AVISO,
  não entra; link do JURIS que abre **outra peça** (`id=` diferente do `id_documento`
  da ficha) → ERRO. Esse último é erro real: uma ficha guardou o id do acórdão com o
  link do relatório de outro documento do mesmo número. Desde 14/09/2026: link de
  domínio de **outro tribunal** que não o da ficha → ERRO (link do JURIS/TJRO numa
  ficha `"tribunal": "TCE-RO"`, ou vice-versa — os dois são domínio oficial, mas do
  tribunal errado; só cobre TJRO e TCE-RO, os que têm MCP próprio com host conhecido).
  TCE-RO **não tem** a proteção "id= diferente" do JURIS — o link do PDF é um hash
  opaco, sem o id da decisão embutido; a defesa contra link da decisão errada sob o
  mesmo número de acórdão é só disciplina de quem monta a ficha (sempre
  `obter_acordao_tcero(id_decisao=...)` específico, nunca copiar link de uma busca
  ambígua por número).

Campos na raiz do JSON:

- `"precedentes"`: lista de fichas (ou caminho de um JSON com a lista). Vem do
  agente `pesquisador-juridico` (uma ficha por julgado) ou do `segundo-cerebro`.
- `"processos_do_caso"`: números CNJ do PRÓPRIO caso que a peça menciona como
  fato (a querela, o agravo de origem) — ficam fora do lint. O número do bloco
  `processo` entra sozinho.
- `"ignorar_citacoes"`: chaves a ignorar pontualmente (falso positivo, ex.:
  `["Tema 3"]` quando "tema 3" é o item de uma pauta).
- `"permitir_nao_verificado": true`: todo ERRO vira AVISO e a peça sai.
  **Último caso, e sempre dizendo ao usuário que a peça saiu com citação não
  conferida.**

Esquema da ficha (é o contrato do `pesquisador-juridico`; respeite os nomes):

```json
{"chave": "AI 0819477-50.2024.8.22.0000", "numero": "0819477-50.2024.8.22.0000",
 "tribunal": "TJRO", "orgao": "2ª Câmara Cível", "orgao_fonte": "fecho | cabeçalho | índice",
 "relator": "Des. Alexandre Miguel",
 "relator_para_acordao": null, "julgamento": "2025-11-07", "publicacao": null,
 "tipo_decisao": "acórdão em embargos de declaração", "id_documento": "30009487",
 "link": "https://juris.tjro.jus.br/jurisprudencia/?id=30009487",
 "outras_decisoes_no_mesmo_numero": ["2026-04-29 — 2º ED rejeitados (Rel. Gurgel do Amaral)"],
 "dispositivo": "texto literal ou null", "tese": "literal, só repetitivo/súmula/IRDR, ou null",
 "ementa": null, "trecho": "trecho literal, cortes com [...]",
 "fatos_relevantes": ["2 a 4 fatos materiais de que a ratio depende"],
 "ratio_ou_dictum": "ratio | dictum | indeterminado",
 "sustenta": "uma linha, nunca mais ampla que o trecho",
 "limites": "a condição da ratio e o que o julgado NÃO sustenta",
 "overruling_status": "vigente | superado por X | não checado",
 "verificado_em": "2026-09-04",
 "verificacao": "inteiro teor lido", "fonte_verificacao": "MCP TJRO — texto do acórdão"}
```

Estes são os nomes **canônicos**, compartilhados com o `pesquisador-juridico` (que produz
a ficha), o `segundo-cerebro` e o template `Ficha-jurisprudência` do vault (que a guardam).
Esta seção é a fonte da tabela: as outras skills remetem a ela em vez de repeti-la.

Fichas antigas do vault e do acervo usam outros nomes, e o lint os **lê** por sinônimo:
`doc_id` → `id_documento`, `data_julgamento` → `julgamento`, `data_publicacao` →
`publicacao`, `orgao_julgador` → `orgao`, `superacao` ou `status` → `overruling_status`.
Ficha nova escreve só o canônico. `fatos_relevantes`, `ratio_ou_dictum`, `limites` e
`overruling_status` não são conferidos pelo lint (ele não tem como): servem ao
distinguishing, que é trabalho do `mapa-de-caso`, e à decisão de usar ou não o precedente.

Regras de redação que o lint pressupõe:

1. **A linha de citação é cópia da ficha** (número + relator + data; TJRO
   também o id do documento), nunca remontada à mão. Um número de processo pode
   ter vários julgados: a decisão se identifica por número + data + id.
2. **Tese de repetitivo, súmula ou IRDR entra literal** num bloco `citacao`; o
   que a peça infere dela vai num `paragrafo` separado ("daí decorre", "a
   contrario sensu"), fora das aspas e da atribuição.
3. **O resultado do julgado se descreve com o verbo do tribunal** (conheceu/não
   conheceu, proveu/desproveu, acolheu/rejeitou), nunca com o efeito ("negou
   honorários").
4. **Citação puxada de peça anterior, própria ou alheia, é NÃO verificada** até
   ser reaberta — protocolo antigo não vale como conferência.
5. Transcrição literal de julgado vai em bloco `citacao` (é onde a literalidade
   é conferida); citação embutida em `paragrafo` só é checada quanto a relator,
   data e órgão.

**O que o lint NÃO garante.** Ele confere a peça contra a **ficha** — consistência,
não veracidade. Ficha com data, relator ou órgão errados passa limpa, e a peça sai
com o erro da ficha. Aconteceu em 08/09/2026: a ficha de um acórdão do TJRO trazia
11/04 no lugar de 16/04/2025, e só a reconferência no MCP TJRO pegou. Portanto: o
"Lint de citações: 0 erro" no build significa "a peça não contradiz as fichas", nunca
"as citações estão certas". Quem responde pela ficha é quem a produziu (o
`pesquisador-juridico`, lendo o inteiro teor) — o lint só impede que a peça se afaste
dela.

Para testar o lint sozinho: `python3 scripts/lint_citacoes.py peca.json`
(código de saída 2 = há erro) ou `--selftest`.

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
- **Hifenização automática: LIGADA** (`<w:autoHyphenation/>` em
  `settings.xml`, regra do usuário, ago/2026). Histórico: tinha sido
  desligada em jul/2026 porque corrompia palavras justificadas no PDF
  ("advogado" → "advo-"/"-ado", com perda de letra). Reativada e testada
  rigorosamente em ago/2026 contra as duas ferramentas de conversão do
  `docx2pdf.sh` — LibreOffice e Word — com texto propositalmente
  desenhado para forçar "advogado" a cair bem na borda da linha: em
  ambas, a quebra saiu limpa e correta ("advo-" / "gado", sem perda de
  caractere). O bug antigo não reproduz mais; a causa raiz original
  provavelmente estava ligada ao pipeline antigo do `docx2pdf.sh` (cópia
  para o sandbox do Word), já removido por outro motivo antes desta
  correção.
  - **Dependência de máquina, fora da skill**: para o LibreOffice
    hifenizar de fato (não só não quebrar — ele silenciosamente NÃO
    hifeniza nada se faltar o dicionário), é preciso o dicionário de
    hifenização em português instalado no perfil do usuário do
    LibreOffice. Instalado em ago/2026 via extensão oficial do portal
    `extensions.libreoffice.org` ("Português do Brasil Spellcheck",
    projeto VERO) — baixado o `.oxt` completo, mas instalado só um
    `.oxt` reduzido (removendo o componente de verificação gramatical
    "Lightproof", que falhava no registro via `unopkg` por um erro de
    pipe UNO) contendo só `dictionaries.xcu` + `hyph_pt_BR.dic` +
    `pt_BR.aff`/`pt_BR.dic`, instalado com `unopkg add` (escopo de
    usuário, não `--shared` — isso precisaria de permissão de escrita no
    bundle assinado do app, que falha e não deve ser tentado). Isso é uma
    dependência **da máquina**, não da skill/DOCX — se a skill for usada
    numa máquina nova (ou no ambiente cloud do Cowork, que não tem nem
    Word nem LibreOffice), a hifenização não vai aparecer no PDF a menos
    que o dicionário seja reinstalado lá. O Word (se presente) já
    hifeniza pt-BR nativamente, sem depender de nada extra.
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
