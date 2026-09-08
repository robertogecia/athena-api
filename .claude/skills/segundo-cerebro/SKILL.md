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

## Depositar

O gatilho é **a tese foi de fato usada numa peça** — não precisa esperar o desfecho do processo para registrar (isso pode levar meses ou anos), mas também não guarde tese só cogitada e descartada. Pergunte se o usuário quer guardar; não decida sozinho o que entra — é filtro consciente, não arquivamento automático.

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

Autoridade, mesma escala do `pesquisador-juridico`/JusRatio — repetida aqui porque esta nota precisa fazer sentido sozinha, sem depender de nenhuma ferramenta estar conectada: **A** vinculante forte (Súmula Vinculante, ADI/ADC/ADPF, Súmula STF/STJ/TST/TSE) · **B** precedente qualificado (Tema Repetitivo, Repercussão Geral, IRDR/IAC) · **C** observância qualificada (Plenário/Corte Especial) · **D** orientativo (acórdão de turma comum, como a maioria) · **E** editorial (informativo).

O trecho da ementa é **cópia do que foi lido** — nunca reconstrução de "o que provavelmente diz". Sem o texto em mãos, deixe em branco e marque `PENDENTE: abrir o acórdão antes de citar em peça` — vale para a ementa, para a `url`, e para qualquer outro campo que não foi de fato conferido. Nota incompleta e sinalizada é infinitamente melhor que nota completa e inventada.

**Tese** (`teses/<slug>.md`):

```markdown
---
tipo: tese
enunciado: "Em uma frase"
autoridade_da_base: solida   # solida = 2+ precedentes independentes · isolada = 1 só · sem_apoio
precedentes_favoraveis: [stj-resp-1234567-forca-maior]
contra_teses: []
resultado_em_juizo: "0 procedentes - 0 improcedentes"   # decisão de mérito real, não contagem de precedentes
ultima_revisao: 2026-08-14
---
```

`autoridade_da_base` só vira `solida` com **dois precedentes de julgamentos independentes** — duas citações do mesmo acórdão em fontes diferentes não contam como duas fontes. É a regra de maior impacto que o `claude-obsidian` valida: afirmação de risco (uma tese que vai sustentar um pedido de verdade) exige corroboração, não uma fonte só.

`resultado_em_juizo` conta **decisões de mérito reais** que aplicaram a tese, não quantos precedentes a sustentam — os dois números não têm relação nenhuma, e confundi-los é o erro mais fácil de cometer aqui. Tese nova começa em `0-0`; só muda quando um `casos/` associado a ela sair de `pendente`.

**Caso** (`casos/<slug>.md`):

```markdown
---
tipo: caso
data: 2026-08-14
tese_usada: [inadimplemento-atraso-obra-cdc]
resultado: pendente   # pendente · procedente · improcedente · acordo · outro
---

Três a cinco linhas: qual tese foi usada, o que o juízo decidiu (ou "ainda sem decisão"), o que faria diferente. Não é o processo; é a lição.
```

Se as partes não foram nomeadas na conversa, não invente — use um slug temático (`2026-atraso-obra-clausula-tolerancia`) em vez de um com nome de cliente. `resultado: pendente` é estado normal, não erro: quando o desfecho sair, volte nesta mesma nota, atualize `resultado` e, se mudou o placar da tese, atualize `resultado_em_juizo` na nota de tese correspondente.

Depois de qualquer depósito — precedente, tese **ou** caso — **atualize `indice.md`** com a linha correspondente. Uma frase curta por entrada (até ~25 palavras): o índice só cumpre a função de evitar reler tudo se ele próprio ficar pequeno. Se um tipo de nota passar de umas 40-50 linhas no índice, considere um índice por pasta em vez de um só.

## Lint (sob pedido, não automático)

Quando o usuário pedir para conferir a base ("faz o lint do segundo cérebro", "confere se tá tudo em dia"), **rode o script** — não confira à mão:

```bash
python3 scripts/lint.py
```

As regras não pedem julgamento nenhum: comparar datas, resolver referências, achar slug no índice, contar precedentes. Cada uma tem exatamente uma resposta certa. Conferir isso lendo arquivo é caro, lento e erra — sobretudo a regra 4, que é a mais fácil de aplicar errado de cabeça.

O que o script confere:

| Rótulo | Regra |
|---|---|
| `RECONFIRMAR` | precedente com `verificado_em` de mais de 6 meses — súmula cancelada e tema superado não avisam ninguém |
| `REBAIXAR` | tese cujos `precedentes_favoraveis` incluem precedente `status: superado` |
| `FORA-DO-INDICE` | nota em `raw/`, `precedentes/`, `teses/` ou `casos/` sem linha em `indice.md` |
| `ARQUIVAR?` | teste dos 30 dias, com **referência transitiva**: um precedente conta como referenciado se a tese que ele sustenta está associada a algum `casos/` pelo campo `tese_usada`, mesmo que nenhum `casos/` cite o slug dele. Sem isso todo precedente vira "órfão" justamente enquanto sustenta a única tese em uso |
| `BASE-FRACA` | `autoridade_da_base: solida` com menos de dois precedentes listados |
| `REF-QUEBRADA` | `precedentes_favoraveis` ou `tese_usada` apontando para nota que não existe |
| `STATUS?` | `status` que não é nem vigente nem superado/cancelado/revogado — o lint não sabe se a tese apoiada nele deve cair |
| `PENDENTE` | marcador `PENDENTE:` deixado na nota — campo não conferido, não citar em peça assim |
| `MALFORMADO` | nota vazia, sem frontmatter, com frontmatter não fechado, lista aberta e não fechada, `verificado_em` ausente ou no futuro, `tipo:` divergente da pasta, ou dois arquivos com o mesmo slug (a referência fica ambígua) |

Saída: `0` nada a fazer · `1` há pendências · `2` há erro estrutural.

`raw/` é fonte bruta — acórdão colado, trecho de doutrina — e não tem frontmatter. Ela entra só na conferência de índice; nenhuma regra de schema se aplica a ela.

**O que o script não confere, e você precisa saber que ele não confere:** se dois precedentes vêm de julgamentos de fato independentes (ele conta dois slugs, não sabe se são o mesmo acórdão citado em duas fontes), se a tese continua fazendo sentido, se o precedente é aplicável ao seu caso. Isso é leitura sua. O script derruba o trabalho mecânico para sobrar tempo justamente para essa parte.

Se um dia mexer no script, rode antes a suíte de regressão:

```bash
python3 scripts/testes/rodar.py
```

São onze casos, cada um a reprodução de um defeito que o lint já teve — inclusive o pior deles, em que `PENDENTE` casava dentro de INDEPENDENTEMENTE e acusava de "não conferido" um precedente em ordem. Dois casos existem para ficar **limpos**: são a conferência de falso positivo, que é o que faz um lint ser ignorado.

O script lê arquivos locais e escreve na tela. Sem rede, sem dependência externa, nada sai da máquina — o que importa, porque `raw/` pode ter trecho colado de autos.

Não rode isso sozinho a cada sessão — é comando do usuário, não hook automático (nada aqui executa sozinho; ver a ressalva de sigilo abaixo).

## Regra dura — herdada do mapa-de-caso, sem exceção aqui

Nunca entra em `precedentes/` julgado que não foi verificado nesta sessão (pelo `pesquisador-juridico`, pelo JusRatio, ou por conferência manual do próprio advogado) ou que já não estivesse, com a mesma verificação, guardado aqui antes. Citação de memória não vira exceção só porque "já vi isso antes" — se não tem nota com `verificado_em`, não existe para efeito de citar.

## Sigilo

Mesma regra do `mapa-de-caso`: nunca publique nota daqui como artifact ou página web — mesmo um precedente público, cruzado com "como foi usado" num caso, identifica cliente. `raw/` em especial pode conter trecho colado de autos; trate como o arquivo mais sensível da pasta.

## Integração

- **`mapa-de-caso`**: consulta este acervo na Etapa 4 (antes de delegar pesquisa) e oferece depositar na Etapa 6 (ao entregar). Ver `delegacao.md` da skill `mapa-de-caso` para o texto de referência.
- **`pesquisador-juridico`**: é quem verifica o que entra aqui — a regra de citação dele (Etapa 4 do mapa, "Delegar a pesquisa") é a mesma regra deste arquivo. Ele não tem ferramenta de arquivo, então nunca lê nem escreve neste acervo diretamente — quem faz isso é sempre a conversa principal.
- **`peticao-rg`**: não interage com o segundo cérebro; formata o documento final, que já não depende mais desta base.
