<!--
Template para ~/.claude/CLAUDE.md (memória pessoal do Claude Code — lida em TODA
sessão, em qualquer pasta, diferente das skills que só entram quando o pedido bate
com a descrição delas).

Se você já tem um ~/.claude/CLAUDE.md, cole o bloco abaixo dentro dele em vez de
substituir. Este arquivo não é o CLAUDE.md do athena-api — é só onde guardo uma
cópia versionada do que te enviei, para não se perder.
-->

# Contexto pessoal — Roberto Grécia Advocacia

OAB: [preencher] · Comarca(s) principal(is): [preencher — ex.: Porto Velho/RO]

## Ecossistema de peças jurídicas

Quatro peças que trabalham juntas, instaladas em `~/.claude/skills/` e `~/.claude/agents/`:

| Quando | O quê |
|---|---|
| Antes de redigir peça em caso com mais de um fato, prova ou pedido | `mapa-de-caso` — monta o grafo do caso e as lacunas antes de escrever |
| Pesquisa de jurisprudência/doutrina, leitura de documento pesado | subagentes `pesquisador-juridico` e `leitor-de-autos` — o `mapa-de-caso` já delega a eles |
| "já usei essa tese antes?", guardar tese ou precedente para depois | `segundo-cerebro` (vive em `~/segundo-cerebro/`) — o `mapa-de-caso` consulta antes de pesquisar |
| Documento final, timbrado | `peticao-rg` |

**Se a pasta da sessão tem PDFs de autos (inicial, contrato, decisão, laudo) e não parece projeto de código, é provável que seja um caso** — considere `mapa-de-caso` mesmo que o pedido não use a palavra "mapa" (ex.: "organiza esse processo", "o que temos de prova aqui", "monta a contestação").

## Quanto de esforço usar em cada caso

Não force multiagente/pipeline em todo caso — a maioria não precisa, e orquestração pesada sem necessidade só custa tempo e tokens. Escale de acordo com o que o caso realmente tem:

| Tamanho do caso | O que usar |
|---|---|
| Poucos documentos, 1-2 teses | `mapa-de-caso` direto, sem delegar nada — cabe tudo numa análise só |
| Pesquisa de jurisprudência, leitura de PDF pesado, mais de uma tese | `mapa-de-caso` delega aos subagentes nomeados (`pesquisador-juridico`, `leitor-de-autos`) em paralelo — é o caso comum |
| Muitos documentos, muitos réus, muitos pedidos (≳10 frentes independentes) | aí sim vale perguntar se cabe um workflow de agentes maior — mas é exceção, não ponto de partida |

O grafo (mapa do caso) é sempre a etapa certa antes de redigir — isso não é "esforço extra", é o método. O que se calibra é só *quanto* delegar dentro dele.

## Regras que valem em qualquer sessão, com ou sem skill ativa

- **Nunca cite jurisprudência de memória** — número de processo, súmula, tema, relator. Só o que foi pesquisado nesta sessão ou já está com `verificado_em` no segundo cérebro. "Não localizado" é resposta completa.
- **Nunca publique conteúdo de um caso como artifact, página web ou link hospedado** — nome de parte, valor da causa e estratégia identificam o cliente, mesmo em link "privado".
- A decisão sobre teses, pedidos e protocolo é sempre sua. Qualquer saída de IA é rascunho para revisão — nunca parecer pronto para assinar.
