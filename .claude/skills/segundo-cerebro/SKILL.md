---
name: segundo-cerebro
description: >-
  Mantém uma base de conhecimento pessoal em markdown puro — teses jurídicas,
  precedentes verificados e o retrospecto de casos anteriores — que o
  mapa-de-caso consulta antes de pesquisar do zero e alimenta depois de cada
  caso encerrado. Use quando o usuário pedir para guardar, salvar ou registrar
  uma tese ou precedente para uso futuro; quando perguntar o que já se sabe
  sobre um tema, tribunal ou tese ("já usei essa tese antes?", "o que já
  pesquisei sobre isso?"); ou quando pedir para conferir/atualizar
  (lint) o que está guardado. Não é o lugar de um caso em andamento — isso é
  o mapa-de-caso; aqui só entra o que já foi usado numa peça de verdade.
---

# Segundo Cérebro

Cada caso que passa pelo `mapa-de-caso` pesquisa jurisprudência do zero — e no caso seguinte, se a tese se repetir, pesquisa tudo de novo. Este é o lugar onde o que já foi verificado uma vez fica disponível para o próximo caso, sem pesquisa nova e sem repetir custo de cota.

O padrão vem de uma prática documentada por Andrej Karpathy e amadurecida por implementações como [AgriciDaniel/claude-obsidian](https://github.com/AgriciDaniel/claude-obsidian) (10,9 mil estrelas): fontes brutas imutáveis separadas do conhecimento processado, e a regra que mais importa aqui — **recusa fundamentada é preferível a citação inventada**. Esta skill porta o padrão como markdown puro, sem instalar o pacote deles: nada de terceiro rodando sobre dados de cliente que você não auditou.

## O que NÃO é

Não é onde um caso ativo vive — isso é o `mapa-de-caso`, e os autos continuam só na pasta do caso. Não é RAG nem banco vetorial — é markdown lido direto, e funciona bem até algumas centenas de notas; se passar disso, revisite o desenho. Não é lugar para "guardar por precaução" — é o inverso do impulso natural de arquivar tudo: **só entra o que já foi usado numa peça de verdade**. Base cheia de coisa nunca reaproveitada é a forma mais comum desse tipo de sistema morrer.

## Onde vive

`~/segundo-cerebro/` — pasta pessoal, irmã de `~/.claude/`, a mesma para qualquer caso, em qualquer sessão. Se não existir, crie na primeira vez que for depositar algo (nunca ao só consultar — consulta em pasta vazia é só "nada encontrado ainda").

```
~/segundo-cerebro/
├── indice.md          # uma linha por nota — o único arquivo lido por inteiro sempre
├── raw/                # fontes brutas, imutáveis: acórdão colado na íntegra, trecho de doutrina
│   └── 2026/stj-resp-1234567.md
├── precedentes/         # só julgado VERIFICADO nesta sessão ou já existente aqui — nunca de memória
│   └── stj-resp-1234567-forca-maior.md
├── teses/               # uma tese por arquivo
│   └── inadimplemento-atraso-obra-cdc.md
└── casos/                # retrospecto breve — não os autos
    └── 2026-silva-x-banco.md
```

Uma nota por tese/precedente/caso, não um arquivo crescente — é o que evita que a base vire o tipo de contexto longo que degrada desempenho do modelo à medida que cresce (context rot). O `indice.md` é o que substitui ler tudo: uma linha por nota, sempre carregado; o resto só sob demanda, quando o índice aponta para ele.

## Consultar (antes de pesquisar)

Sempre que o `mapa-de-caso` for delegar uma pesquisa de jurisprudência (Frente 1 de `delegacao.md`), primeiro:

1. Leia `indice.md`.
2. Se a tese já tem nota em `teses/`, abra-a — ela já lista os precedentes favoráveis e contrários, com `status` de cada um.
3. **Todo precedente da nota carrega `verificado_em`.** Se estiver com mais de 6 meses, trate como pendência de reconfirmação — não como pesquisa dispensada. Súmula cancelada e tema superado não avisam ninguém.
4. Só delegue pesquisa nova para o que a nota não cobre, ou para reconfirmar o que passou do prazo.

Isso substitui pesquisa nova por leitura de nota quando a nota já responde — e é o ganho real de manter isso: o segundo caso sobre a mesma tese começa rico, não do zero.

## Depositar (depois de um caso encerrado)

Ao final de um caso — quando a peça foi protocolada e o desfecho é conhecido, ou pelo menos quando a tese foi de fato usada, não só cogitada — pergunte se o usuário quer guardar. Não decida sozinho o que entra; é filtro consciente, não arquivamento automático.

**Precedente** (`precedentes/<slug>.md`):

```markdown
---
tipo: precedente
tribunal: STJ
orgao: Terceira Turma
classe_numero: REsp 1.234.567/SP
relator: Nancy Andrighi
julgamento: 2026-03-12
autoridade: B
url: https://...
verificado_em: 2026-08-14
status: vigente
teses: [inadimplemento-atraso-obra-cdc]
---

## Ementa (trecho literal)

## Como foi usado
[[2026-silva-x-banco]] — item 3.2, sustentou T1
```

**Tese** (`teses/<slug>.md`):

```markdown
---
tipo: tese
enunciado: "Em uma frase"
autoridade_da_base: solida   # solida = 2+ precedentes independentes · isolada = 1 só · sem_apoio
precedentes_favoraveis: [stj-resp-1234567-forca-maior]
contra_teses: []
placar: "1-0"
ultima_revisao: 2026-08-14
---
```

`autoridade_da_base` só vira `solida` com **dois precedentes de julgamentos independentes** — duas citações do mesmo acórdão em fontes diferentes não contam como duas fontes. É a regra de maior impacto que o `claude-obsidian` valida: afirmação de risco (uma tese que vai sustentar um pedido de verdade) exige corroboração, não uma fonte só.

**Caso** (`casos/<slug>.md`): três a cinco linhas — qual tese foi usada, o que o juízo decidiu, o que faria diferente. Não é o processo; é a lição.

Depois de qualquer depósito, **atualize `indice.md`** com a linha correspondente — nota sem entrada no índice é nota que ninguém vai achar.

## Lint (sob pedido, não automático)

Quando o usuário pedir para conferir a base ("faz o lint do segundo cérebro", "confere se tá tudo em dia"):

1. Toda nota em `precedentes/` com `verificado_em` de mais de 6 meses → listar para reconfirmação.
2. Toda `tese` cujos `precedentes_favoraveis` incluam um precedente marcado `status: superado` → rebaixar `autoridade_da_base` e sinalizar.
3. Nota em `raw/`, `precedentes/` ou `teses/` sem entrada correspondente em `indice.md` → adicionar ou perguntar se deve ser removida.
4. Teste dos 30 dias: nota em `teses/` ou `precedentes/` nunca referenciada por nenhum caso em `casos/` desde que foi criada → candidata a arquivar. Base que só cresce e nunca poda é a mesma que vira pasta morta.

Não rode isso sozinho a cada sessão — é comando do usuário, não hook automático (nada aqui executa sozinho; ver a ressalva de sigilo abaixo).

## Regra dura — herdada do mapa-de-caso, sem exceção aqui

Nunca entra em `precedentes/` julgado que não foi verificado nesta sessão (pelo `pesquisador-juridico`, pelo JusRatio, ou por conferência manual do próprio advogado) ou que já não estivesse, com a mesma verificação, guardado aqui antes. Citação de memória não vira exceção só porque "já vi isso antes" — se não tem nota com `verificado_em`, não existe para efeito de citar.

## Sigilo

Mesma regra do `mapa-de-caso`: nunca publique nota daqui como artifact ou página web — mesmo um precedente público, cruzado com "como foi usado" num caso, identifica cliente. `raw/` em especial pode conter trecho colado de autos; trate como o arquivo mais sensível da pasta.

## Integração

- **`mapa-de-caso`**: consulta este acervo na Etapa 4 (antes de delegar pesquisa) e oferece depositar na Etapa 6 (ao entregar). Ver `delegacao.md` da skill `mapa-de-caso` para o texto de referência.
- **`pesquisador-juridico`**: é quem verifica o que entra aqui — a regra de citação dele (Etapa 5 do mapa) é a mesma regra deste arquivo.
- **`peticao-rg`**: não interage com o segundo cérebro; formata o documento final, que já não depende mais desta base.
