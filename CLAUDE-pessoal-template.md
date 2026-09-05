<!--
Template para ~/.claude/CLAUDE.md (memória pessoal do Claude Code — lida em TODA
sessão, em qualquer pasta, diferente das skills que só entram quando o pedido bate
com a descrição delas).

Se você já tem um ~/.claude/CLAUDE.md, cole o bloco abaixo dentro dele em vez de
substituir. Este arquivo não é o CLAUDE.md do athena-api — é só onde guardo uma
cópia versionada do que te enviei, para não se perder.
-->

# Contexto pessoal — Roberto Grécia Advocacia

Roberto Grécia Bessa · OAB/RO 7865 · Comarca(s) principal(is): [preencher]

## Ecossistema de peças jurídicas

Quatro peças que trabalham juntas, instaladas em `~/.claude/skills/` e `~/.claude/agents/`:

| Quando | O quê |
|---|---|
| Antes de redigir peça em caso com mais de um fato, prova ou pedido | `mapa-de-caso` — monta o grafo do caso e as lacunas antes de escrever |
| Pesquisa de jurisprudência/doutrina, leitura de documento pesado | subagentes `pesquisador-juridico` e `leitor-de-autos` — o `mapa-de-caso` já delega a eles |
| "já usei essa tese antes?", guardar tese ou precedente para depois | `segundo-cerebro` (vive em `~/segundo-cerebro/`) — o `mapa-de-caso` consulta antes de pesquisar |
| Documento final, timbrado | `peticao-rg` |

**Se a pasta da sessão tem PDFs de autos (inicial, contrato, decisão, laudo) e não parece projeto de código, é provável que seja um caso** — considere `mapa-de-caso` mesmo que o pedido não use a palavra "mapa" (ex.: "organiza esse processo", "o que temos de prova aqui", "monta a contestação").

**Ordem entre `mapa-de-caso` e `peticao-rg`**: as duas reivindicam "redija a contestação", então vale a regra explícita — o `mapa-de-caso` vem primeiro, sempre. A `peticao-rg` formata o que já foi decidido; não decide o que escrever. E não gere o documento final timbrado enquanto houver 🔴 aberto no mapa: peça bem diagramada em cima de lacuna não resolvida é pior que peça nenhuma, porque parece pronta para assinar.

## Quanto de esforço usar em cada caso

Não force multiagente/pipeline em todo caso — a maioria não precisa, e orquestração pesada sem necessidade só custa tempo e tokens sem ganho.

**Antes de contar teses e documentos para decidir a escala, consulte o `segundo-cerebro`.** Ele existe para encolher essa conta: tese com nota lá, `verificado_em` dentro de 6 meses, não entra como "precisa de pesquisa" — já está resolvida, só falta ler. Só depois de descontar o que o acervo já responde, escale pelo que sobrou:

- **1 fato, 1 prova, 1 pedido, sem documento pesado e sem pesquisa pendente**: `mapa-de-caso` direto, sem delegar nada — cabe tudo numa análise só.
- **2 ou mais teses ainda sem nota verificada no segundo cérebro, documento pesado (laudo, contrato longo), ou precisa de pesquisa de jurisprudência/doutrina**: `mapa-de-caso` delega aos subagentes nomeados (`pesquisador-juridico`, `leitor-de-autos`) em paralelo — é o caso comum.
- **Muitas partes com posição própria a comparar** (litisconsórcio numeroso, concurso de credores em falência/recuperação/inventário) **ou muitos documentos**: aí sim vale perguntar se cabe um workflow de agentes maior para a etapa de leitura e pesquisa — o limiar exato de quando isso compensa está em `references/delegacao.md` do `mapa-de-caso`; não repito o número aqui para as duas referências não desalinharem com o tempo.

**Mesmo delegando a coleta, a comparação final é sempre sua.** Agentes em paralelo não conversam entre si — cruzar 8 posições numa única ordem de prioridade não vira 8 pareceres paralelos costurados depois; a leitura e a pesquisa paralelizam, o julgamento sobre como elas se relacionam não.

**Só a conversa principal toca o `segundo-cerebro`.** `pesquisador-juridico` e `leitor-de-autos` não têm acesso de leitura à pasta — eles verificam e devolvem o que encontram; quem lê o acervo antes de delegar e quem escreve nele depois (só com confirmação do usuário) é sempre a conversa principal, nunca um subagente isolado decidindo sozinho o que entra.

O grafo (mapa do caso) é sempre a etapa certa antes de redigir — isso não é "esforço extra", é o método. O que se calibra é só *quanto* delegar dentro dele, depois de checar o que o segundo cérebro já resolve.

## Regras que valem em qualquer sessão, com ou sem skill ativa

- **Nunca cite jurisprudência de memória** — número de processo, súmula, tema, relator. Só o que foi pesquisado nesta sessão ou já está com `verificado_em` no segundo cérebro. "Não localizado" é resposta completa.
- **Nunca publique conteúdo de um caso como artifact, página web ou link hospedado** — nome de parte, valor da causa e estratégia identificam o cliente, mesmo em link "privado".
- A decisão sobre teses, pedidos e protocolo é sempre sua. Qualquer saída de IA é rascunho para revisão — nunca parecer pronto para assinar.
