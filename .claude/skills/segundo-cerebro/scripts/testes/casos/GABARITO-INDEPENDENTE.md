# Gabarito — fixtures de lint do segundo-cérebro

Construído **apenas** a partir da especificação em prosa
(`.claude/skills/segundo-cerebro/SKILL.md`), sem ler nenhuma implementação.
Data de referência para todos os cálculos de prazo: **2026-09-08**. Limiar
da regra "mais de 6 meses" (item 1 do Lint): qualquer `verificado_em`
anterior a **2026-03-08** viola a regra.

Todos os números de processo, relatores, temas e nomes de tribunal são
fictícios. Nenhum dado real, nenhum nome de cliente.

## 0. Decisões de interpretação

A especificação não é 100% explícita em três pontos. Registro aqui a
leitura adotada para montar as fixtures, para que o gabarito não dependa
de uma leitura que o implementador não compartilhe:

1. **"Teste dos 30 dias" (regra 4) — o que conta como "desde que criados".**
   O texto nomeia a regra "teste dos 30 dias" mas não define
   explicitamente qual campo de data mede a idade da nota, e nem
   `precedentes/` nem `teses/` têm um campo `criado_em` no schema. Para
   não depender dessa leitura, **toda nota que não está testando a regra
   4 tem associação real e direta com algum `casos/` via `tese_usada`** —
   ou seja, o "nunca associada" da regra é literalmente falso para ela,
   e a ambiguidade do prazo de 30 dias não chega a ser acionada. Só as
   duas notas do cluster de órfão genuíno (`redirecionamento-execucao-
   fiscal-dissolucao-irregular` e o precedente que a sustenta) dependem
   da leitura de prazo — e lá as datas (`verificado_em`/`ultima_revisao`
   em torno de 2026-06/07) estão confortavelmente a mais de 30 dias de
   2026-09-08 por qualquer cálculo razoável, e a mais de um mês dentro
   da janela dos 6 meses (para não disparar também a regra 1 por engano).
2. **`resultado_em_juizo` confundido com contagem de precedentes.** Não é
   uma das 4 regras numeradas em "## Lint" — é dita em prosa na seção
   "Depositar" ("os dois números não têm relação nenhuma, e confundi-los
   é o erro mais fácil de cometer aqui"). Tratado abaixo como achado
   "bônus": um lint mínimo (só as 4 regras numeradas) não é obrigado a
   pegá-lo, mas um lint fiel ao espírito da especificação deveria.
3. **Regra dura de verificação-em-sessão.** "Nunca entra em `precedentes/`
   julgado que não foi verificado nesta sessão..." descreve um processo,
   não uma propriedade do arquivo — não dá para provar estaticamente,
   lendo só o markdown, que uma verificação aconteceu ou não numa sessão
   passada. O único sintoma observável em arquivo é o que a regra do
   marcador `PENDENTE` cobre: campo não conferido que ficou em branco
   *sem* o marcador. É esse sintoma que as fixtures testam (achado 11 em
   `acervo-sujo`, e o contraponto correto em `acervo-limpo`).
4. **Regra de slug sem nome de cliente** ("use um slug temático... em vez
   de um com nome de cliente") não foi violada de propósito em nenhuma
   fixture: as regras de conteúdo desta própria tarefa proíbem nome de
   cliente em qualquer arquivo, real ou fictício, então não há como
   construir esse caso sem contrariar a própria tarefa. Fora do escopo
   destas fixtures.
5. A observação "se um tipo de nota passar de 40-50 linhas no índice,
   considere um índice por pasta" é uma sugestão de design ("considere"),
   não uma regra de conferência — não é testada aqui.

---

## 1. `acervo-limpo/` — resultado esperado: **nenhum achado**

9 arquivos (8 notas + `indice.md`). Um lint correto, rodado sobre esta
pasta, não deve reportar nada. Lista completa, para conferência de
cobertura:

| Arquivo | Por que está limpo |
|---|---|
| `raw/2026/stj-resp-1111111.md` | Indexado, sem frontmatter (não é exigido em `raw/`). |
| `precedentes/stj-resp-1111111-atraso-obra-tolerancia.md` | `verificado_em: 2026-08-10` (< 6 meses), `status: vigente`, indexado, ementa e url preenchidas de fato. |
| `precedentes/stj-resp-2222222-atraso-obra-tolerancia.md` | `verificado_em: 2026-07-22` (< 6 meses), `status: vigente`, indexado; julgamento independente do anterior (turma, relator e data diferentes). |
| `precedentes/trf1-ac-3333333-tarifa-bancaria-abusiva.md` | `verificado_em: 2026-08-05` (< 6 meses), `status: vigente`, indexado; `url` está com o marcador `PENDENTE:` corretamente — isso **não** é achado, é o uso certo da convenção. |
| `teses/atraso-entrega-imovel-planta-tolerancia.md` | `autoridade_da_base: solida` com **2 precedentes de julgamentos independentes** (turma, relator e data diferentes) — sólida de verdade. `resultado_em_juizo: "1 procedentes - 0 improcedentes"` reflete o único caso real (não os 2 precedentes). Associada a um `casos/`. |
| `teses/cobranca-tarifa-bancaria-abusiva-repeticao.md` | `autoridade_da_base: isolada` com exatamente 1 precedente — rótulo correto. `resultado_em_juizo: "0-0"` condizente com o caso ainda pendente. Associada a um `casos/`. |
| `casos/2026-atraso-obra-clausula-tolerancia.md` | `tese_usada` aponta para tese existente e indexada; `resultado: procedente` é decisão de mérito real. |
| `casos/2026-tarifa-bancaria-repeticao-indebito.md` | `resultado: pendente` — estado normal, não erro. |

Todas as 8 notas têm entrada correspondente em `indice.md` (regra 3
satisfeita) e nenhum precedente está com `status: superado` (regra 2
não se aplica).

### 1.1 Armadilhas propositais que NÃO devem virar achado

Estas construções aparecem de propósito para testar se o parser
hand-rolled do lint quebra ou falso-positiva em sintaxe válida-porém-
difícil. Nenhuma delas é um achado:

- **Comentário `#` depois do valor**, no estilo do próprio template da
  especificação: `status: vigente   # confirmado no portal do STJ em
  2026-08-10` (em `stj-resp-1111111-...`) e `autoridade_da_base: solida
  # 2+ precedentes de julgamentos independentes confirmados` /
  `contra_teses: []   # nenhuma tese contrária mapeada até o momento`
  (em `atraso-entrega-imovel-planta-tolerancia.md`). O valor real é
  `vigente` / `solida` / `[]` — o comentário não é dado.
- **Aspas simples vs. duplas**: `relator: 'Des. Fed. Otávio Marambaia'`
  (simples, em `trf1-ac-3333333-...`) e `enunciado: "Atraso além da
  cláusula..."` (duplas, em `atraso-entrega-imovel-planta-tolerancia.md`).
  Ambas devem ser lidas como string, aspas removidas.
- **`#` dentro de string entre aspas**: `enunciado: "Atraso além da
  cláusula de tolerância (item #4 do contrato-padrão) gera dano moral
  presumido..."` — o `#4` faz parte do valor; um parser que corta no
  primeiro `#` da linha (ignorando que está dentro de aspas) vai truncar
  o enunciado errado. Não é achado, é teste de robustez.
- **Lista vazia `[]`**: `contra_teses: []` em ambas as teses. Lista
  vazia válida, não "campo faltando".
- **Valor com `:` no meio (url)**: `url: https://scon.stj.jus.br/SCON/
  GetInteiroTeorDoAcordao?num_registro=2025:0345678-9` (em
  `stj-resp-2222222-...`) — o `:` depois de `num_registro=2025` não pode
  quebrar o parser nem ser confundido com um novo par chave/valor.
- **`PENDENTE:` usado corretamente**: `url: "PENDENTE: link do TRF1
  ainda não localizado"` em `trf1-ac-3333333-tarifa-bancaria-abusiva.md`
  — o campo não foi conferido e está sinalizado como manda a
  especificação. Isso é o comportamento *correto*; sinalizar isso como
  achado seria o falso positivo que a regra do marcador existe para
  evitar. (A ementa do mesmo precedente, em contraste, está preenchida —
  reforça que a sinalização é por campo, não tudo-ou-nada.)

### 1.2 A armadilha da referência transitiva (regra 4)

`precedentes/stj-resp-1111111-atraso-obra-tolerancia.md` e
`precedentes/stj-resp-2222222-atraso-obra-tolerancia.md` sustentam a tese
`atraso-entrega-imovel-planta-tolerancia` (campo `teses:` de cada
precedente, e `precedentes_favoraveis:` da tese, referenciam um ao
outro). Essa tese está associada a `casos/2026-atraso-obra-clausula-
tolerancia.md` via `tese_usada`. **Mas o corpo desse `casos/` nunca cita
o slug de nenhum dos dois precedentes** (nem por wikilink `[[...]]`, nem
por texto) — fala só da tese, em prosa.

Um lint ingênuo que procura o slug do precedente citado literalmente em
algum `casos/*.md` vai marcar os dois precedentes como "órfãos" pela
regra 4 — **isso é o falso positivo que este cenário existe para pegar.**
A especificação é explícita: "a referência é transitiva... mesmo que o
`casos/` nunca cite o slug do precedente diretamente." Um lint correto
segue a cadeia precedente → `teses:` → tese → `precedentes_favoraveis:`
(mesmo slug) → tese usada por `casos/` via `tese_usada` → **referenciado,
não é candidato a arquivar.**

Resultado esperado para os dois precedentes desta tese: **nenhum
achado** pela regra 4.

---

## 2. `acervo-sujo/` — achado por achado

34 arquivos. 17 contêm exatamente a violação descrita abaixo (a maioria
"uma violação por nota", com as duas exceções compostas assinaladas).
Os demais são notas de apoio **sem achado** — ver seção 3, importante
para medir falso positivo dentro do próprio acervo sujo.

### 2.1 Regra 1 — `verificado_em` com mais de 6 meses

| Arquivo | Achado esperado |
|---|---|
| `precedentes/tjro-ac-4444444-vicio-oculto-decadencia.md` | `verificado_em: 2025-10-02` — mais de 6 meses antes de 2026-09-08 (limiar: 2026-03-08). Listar para reconfirmação. Nota: contém `url` com `:` no meio do valor (`?proc=4444444:2025`) e comentário-armadilha não se aplica aqui, é só teste de parsing de url — o único achado real é a data. |

*(Notas de apoio deste cluster, sem achado: `teses/vicio-oculto-bem-movel-prazo-decadencial.md`, `casos/2026-vicio-oculto-bem-movel.md`.)*

### 2.2 Regra 2 — tese `solida` apoiada em precedente `status: superado`

| Arquivo | Achado esperado |
|---|---|
| `teses/foro-eleicao-abusivo-contrato-adesao.md` | `precedentes_favoraveis` inclui `stj-resp-6666666-foro-eleicao-abusivo-superado`, cujo `status` é `superado`. A tese continua `autoridade_da_base: solida`. Deve ser **rebaixada** (sobra só 1 precedente vigente — `stj-resp-7777777-foro-eleicao-abusivo` — ou seja, na prática vira `isolada`) e **sinalizada**. Nota: `enunciado` contém `#3` dentro de aspas duplas — testa o mesmo parser-trap do item 1.1, não é achado à parte. |

*(Notas de apoio: `precedentes/stj-resp-7777777-foro-eleicao-abusivo.md` — vigente, sem achado; `precedentes/stj-resp-6666666-foro-eleicao-abusivo-superado.md` — estar `superado` não é, em si, um achado, é só o fato que dispara o achado na tese; `casos/2026-foro-eleicao-abusivo-contrato-adesao.md` — sem achado, e `resultado: procedente` bate com o `resultado_em_juizo: "1 procedentes - 0 improcedentes"` da tese, então isso não se confunde com o achado da seção 2.8.)*

### 2.3 Regra 3 — nota sem entrada em `indice.md` (uma por pasta)

| Arquivo | Pasta | Achado esperado |
|---|---|---|
| `raw/2026/stj-resp-7777777.md` | `raw/` | Existe no disco, sem linha correspondente em `indice.md`. Adicionar ou perguntar se deve ser removida. |
| `precedentes/stj-resp-8888888-clausula-penal-compensatoria-excessiva.md` | `precedentes/` | Idem. Nota válida e completa (`teses: []` é só o teste de lista vazia, não é achado à parte — um precedente sem tese vinculada ainda não é, por si, violação de nenhuma regra do Lint). |
| `teses/plataforma-digital-responsabilidade-anuncio-fraudulento.md` | `teses/` | Idem. `autoridade_da_base: sem_apoio` com `precedentes_favoraveis: []` é rótulo correto (tese emergente, sem precedente ainda) — não gera achado de solidez. Está associada a um `casos/` (o próprio `casos/2026-plataforma-digital-anuncio-fraudulento.md`), então também não é candidata a órfã pela regra 4. |
| `casos/2026-vicio-oculto-bem-movel-consorcio.md` | `casos/` | Idem. Segundo caso usando a mesma tese do cluster 2.1 — reforça que uma tese pode (e deve) ser reaproveitada; a única falha aqui é não estar no índice. |

### 2.4 Regra 4 — teste dos 30 dias / órfão genuíno (e não-transitivo)

| Arquivo | Achado esperado |
|---|---|
| `teses/redirecionamento-execucao-fiscal-dissolucao-irregular.md` | Nunca associada a nenhum `casos/*.md` via `tese_usada`, em nenhum arquivo do acervo. `ultima_revisao: 2026-06-20` — mais de 30 dias antes de 2026-09-08. Candidata a arquivar. |
| `precedentes/tjro-ac-1010101-dissolucao-irregular-execucao-fiscal.md` | Sustenta (via `teses:`) exatamente a tese acima, que nunca foi usada por nenhum caso — órfão transitivo. `verificado_em: 2026-07-05` — mais de 30 dias antes de hoje (mas propositalmente dentro dos 6 meses, para não também disparar a regra 1 e confundir o achado). Candidato a arquivar. |

Note o contraste com a seção 1.2: aqui não há *nenhum* `casos/` que use a
tese `redirecionamento-execucao-fiscal-dissolucao-irregular` — nem
diretamente, nem transitivamente. É o oposto do cenário do
`acervo-limpo`: lá a ausência de citação direta é enganosa (a tese *é*
usada); aqui a ausência é real (a tese não é usada de jeito nenhum).

### 2.5 Corroboração de `solida` — só 1 precedente

| Arquivo | Achado esperado |
|---|---|
| `teses/plano-saude-inversao-onus-prova-negativa-cobertura.md` | `autoridade_da_base: solida`, mas `precedentes_favoraveis` tem só 1 entrada (`stj-resp-1212121-plano-saude-inversao-onus-prova`). Solida exige 2+ precedentes de julgamentos independentes. Deveria ser `isolada`. |

*(Apoio: `precedentes/stj-resp-1212121-...` e `casos/2026-plano-saude-negativa-cobertura-inversao-onus.md`, ambos sem achado.)*

### 2.6 Corroboração de `solida` — 2 citações do mesmo julgamento (fontes diferentes, não independentes)

| Arquivo | Achado esperado |
|---|---|
| `teses/fraude-cartao-credito-legitimidade-passiva-administradora.md` | `autoridade_da_base: solida` com 2 entradas em `precedentes_favoraveis` (`stj-resp-1313131-fraude-cartao-legitimidade-passiva` e `stj-tema-1313131-fraude-cartao-jusratio`) — mas os dois precedentes têm **o mesmo** `classe_numero` (REsp 1.313.131/SP), `tribunal`, `orgao`, `relator` e `julgamento` (2026-01-20): é o mesmo acórdão, capturado duas vezes por descuido (uma vez manualmente, outra via JusRatio). "Duas citações do mesmo acórdão em fontes diferentes não contam como duas fontes." Deveria ser `isolada`. |

Achado exige comparar `classe_numero`+`tribunal`+`julgamento` entre os
dois precedentes referenciados pela mesma tese — não basta contar
entradas em `precedentes_favoraveis`. As duas notas de precedente
individualmente **não** têm achado (cada uma, isolada, é uma nota válida
e bem verificada); o problema só aparece na composição, na tese.

### 2.7 Campo em branco sem marcador `PENDENTE`

| Arquivo | Achado esperado |
|---|---|
| `precedentes/stj-resp-1414141-negativacao-indevida-apos-quitacao.md` | `url:` em branco e a seção `## Ementa (trecho literal)` em branco — nenhum dos dois tem o marcador `PENDENTE: ...`. Pela regra de sinalização, campo não conferido deve ficar em branco **com** o marcador; aqui está em branco **sem** ele — sintoma de campo não conferido tratado como se fosse dado ausente sem aviso (o mesmo padrão que a "regra dura" de verificação proíbe silenciosamente). Ambos os campos desta nota compartilham o mesmo achado. |

*(Apoio: `teses/negativacao-indevida-apos-quitacao-dano-moral.md` e `casos/2026-negativacao-indevida-apos-quitacao.md`, sem achado.)*

Contraste direto com `acervo-limpo/precedentes/trf1-ac-3333333-
tarifa-bancaria-abusiva.md` (seção 1.1), que deixa `url` em branco *com*
o marcador — e por isso não é achado lá.

### 2.8 Campo obrigatório faltando

| Arquivo | Achado esperado |
|---|---|
| `precedentes/tjro-ac-1515151-honorarios-sucumbenciais-recursais.md` | Frontmatter sem o campo `autoridade` (presente no template da especificação: A/B/C/D/E). Campo obrigatório ausente. |
| `casos/2026-caso-sem-resultado-campo-faltando.md` | Frontmatter tem `tipo`, `data`, `tese_usada`, mas **falta `resultado`** (obrigatório: pendente/procedente/improcedente/acordo/outro). Não deve ser confundido com `resultado: pendente` — aqui o campo simplesmente não existe. |

*(Apoio do primeiro: `teses/honorarios-sucumbenciais-recursais-fixacao-percentual.md` e `casos/2026-honorarios-sucumbenciais-recursais.md`, sem achado. O segundo reaproveita a tese `negativacao-indevida-apos-quitacao-dano-moral` do cluster 2.7 como segundo caso — reforço de reúso de tese, não gera achado na tese.)*

### 2.9 `resultado_em_juizo` confundido com contagem de precedentes (achado "bônus" — ver Decisão de interpretação 2)

| Arquivo | Achado esperado |
|---|---|
| `teses/juros-remuneratorios-abusivos-cartao-consignado.md` | `resultado_em_juizo: "1 procedentes - 0 improcedentes"`, mas o único `casos/` associado (`casos/2026-juros-consignado-abusivos.md`) está com `resultado: pendente` — nenhuma decisão de mérito real ainda. O "1" bate exatamente com o número de entradas em `precedentes_favoraveis` (1), não com decisões reais (0). Contagem de precedente confundida com resultado em juízo. |

### 2.10 Robustez estrutural do parser (fora das 4 regras numeradas, mas exigida pela tarefa)

Estas quatro notas testam se o parser de frontmatter, escrito à mão,
lida com entrada malformada sem quebrar e sem interpretar campos errado.
Nenhuma delas permite aplicar as regras 1/2/4 normalmente — a leitura
correta é reportar a nota como malformada/ilegível antes de mais nada.

| Arquivo | Problema | Achado esperado |
|---|---|---|
| `casos/2026-arquivo-vazio-registro-incompleto.md` | Arquivo com 0 bytes. | Reportar como nota vazia/ilegível. **Também** viola a regra 3 (não está em `indice.md`) — composto de propósito: um arquivo vazio provavelmente nem foi finalizado, então plausivelmente também não foi indexado. |
| `casos/2026-sem-frontmatter-registro-informal.md` | Nenhum bloco `---`/`---`; é só texto corrido. | Reportar como nota sem frontmatter — não dá para extrair `tipo`, `tese_usada` ou `resultado`. Está indexada de propósito (linha própria em `indice.md`), para isolar só este achado (não é também um achado de regra 3). |
| `casos/2026-caso-sem-resultado-campo-faltando.md` | Ver 2.8 — frontmatter válido, mas incompleto. | (já coberto acima) |
| `teses/plano-odontologico-clausula-carencia-abusiva.md` | Bloco `---` de abertura presente, mas nunca fechado — o que deveria ser corpo continua dentro do que parece frontmatter. | Reportar como frontmatter não fechado / nota malformada. Está indexada de propósito para isolar só este achado. O `precedentes_favoraveis: [tjro-ac-1717171-plano-odontologico-carencia]` citado dentro do bloco aponta para um arquivo que não existe no acervo — **incidental**, não é um achado à parte: a nota já está marcada como malformada por causa do frontmatter aberto, então essa referência nunca chega a ser avaliada por uma regra que dependa de frontmatter válido. |

Nenhuma das quatro é, ao mesmo tempo, candidata a órfã pela regra 4 (a
regra 4 vale para `teses/` e `precedentes/`; nenhuma destas quatro é dos
dois tipos que sobrevivem à falha de parsing o suficiente para isso
importar).

---

## 3. Notas de `acervo-sujo/` sem nenhum achado (controle de falso positivo)

Estas 17 notas existem só para dar contexto/isolamento aos achados acima
— nenhuma delas deve gerar achado algum. Um lint que reporta qualquer
uma destas está com falso positivo:

- `precedentes/stj-resp-7777777-foro-eleicao-abusivo.md`
- `precedentes/stj-resp-1212121-plano-saude-inversao-onus-prova.md`
- `precedentes/stj-resp-1313131-fraude-cartao-legitimidade-passiva.md`
- `precedentes/stj-tema-1313131-fraude-cartao-jusratio.md`
- `precedentes/tjro-ac-1515151-honorarios-sucumbenciais-recursais.md`
- `precedentes/stj-resp-1616161-juros-consignado-abusivos.md`
- `teses/vicio-oculto-bem-movel-prazo-decadencial.md`
- `teses/negativacao-indevida-apos-quitacao-dano-moral.md`
- `teses/honorarios-sucumbenciais-recursais-fixacao-percentual.md`
- `casos/2026-vicio-oculto-bem-movel.md`
- `casos/2026-foro-eleicao-abusivo-contrato-adesao.md`
- `casos/2026-plano-saude-negativa-cobertura-inversao-onus.md`
- `casos/2026-plataforma-digital-anuncio-fraudulento.md`
- `casos/2026-fraude-cartao-credito-legitimidade-passiva.md`
- `casos/2026-negativacao-indevida-apos-quitacao.md`
- `casos/2026-honorarios-sucumbenciais-recursais.md`
- `casos/2026-juros-consignado-abusivos.md`

Note que `teses/plano-saude-inversao-onus-prova-negativa-cobertura.md`
**não** está nesta lista de controle — ela é, ela mesma, o achado 2.5
(solida com só 1 precedente). Só as notas de apoio ao redor dela
(o precedente e o caso) é que estão listadas acima como sem achado.

---

## 4. Resumo — uma linha por violação plantada

`arquivo → regra violada`

1. `acervo-sujo/precedentes/tjro-ac-4444444-vicio-oculto-decadencia.md` → Regra 1 (verificado_em com mais de 6 meses: 2025-10-02)
2. `acervo-sujo/teses/foro-eleicao-abusivo-contrato-adesao.md` → Regra 2 (solida apoiada em precedente status: superado; deveria rebaixar para isolada)
3. `acervo-sujo/raw/2026/stj-resp-7777777.md` → Regra 3 (raw/ sem entrada em indice.md)
4. `acervo-sujo/precedentes/stj-resp-8888888-clausula-penal-compensatoria-excessiva.md` → Regra 3 (precedentes/ sem entrada em indice.md)
5. `acervo-sujo/teses/plataforma-digital-responsabilidade-anuncio-fraudulento.md` → Regra 3 (teses/ sem entrada em indice.md)
6. `acervo-sujo/casos/2026-vicio-oculto-bem-movel-consorcio.md` → Regra 3 (casos/ sem entrada em indice.md)
7. `acervo-sujo/teses/redirecionamento-execucao-fiscal-dissolucao-irregular.md` → Regra 4 (tese nunca associada a nenhum casos/, candidata a arquivar)
8. `acervo-sujo/precedentes/tjro-ac-1010101-dissolucao-irregular-execucao-fiscal.md` → Regra 4 (precedente cuja única tese nunca foi usada, órfão transitivo, candidato a arquivar)
9. `acervo-sujo/teses/plano-saude-inversao-onus-prova-negativa-cobertura.md` → Corroboração de solida (só 1 precedente_favoravel, deveria ser isolada)
10. `acervo-sujo/teses/fraude-cartao-credito-legitimidade-passiva-administradora.md` → Corroboração de solida (2 precedentes citados, mas é o mesmo julgamento duas vezes — não são fontes independentes)
11. `acervo-sujo/precedentes/stj-resp-1414141-negativacao-indevida-apos-quitacao.md` → Marcador PENDENTE ausente (ementa e url em branco sem sinalização)
12. `acervo-sujo/precedentes/tjro-ac-1515151-honorarios-sucumbenciais-recursais.md` → Campo obrigatório faltando (autoridade)
13. `acervo-sujo/casos/2026-caso-sem-resultado-campo-faltando.md` → Campo obrigatório faltando (resultado)
14. `acervo-sujo/teses/juros-remuneratorios-abusivos-cartao-consignado.md` → resultado_em_juizo confundido com contagem de precedentes (bônus, fora das 4 regras numeradas)
15. `acervo-sujo/casos/2026-arquivo-vazio-registro-incompleto.md` → Estrutural: arquivo vazio (0 bytes) + Regra 3 (também sem entrada em indice.md)
16. `acervo-sujo/casos/2026-sem-frontmatter-registro-informal.md` → Estrutural: arquivo sem bloco de frontmatter algum
17. `acervo-sujo/teses/plano-odontologico-clausula-carencia-abusiva.md` → Estrutural: frontmatter aberto (`---`) e nunca fechado

`acervo-limpo/` → nenhuma violação plantada; resultado esperado é zero achados, incluindo nos dois casos-armadilha (transitividade da regra 4, seção 1.2; e uso correto do marcador `PENDENTE`, seção 1.1).
