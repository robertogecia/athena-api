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
| Antes de redigir peça em caso com mais de um fato, prova ou pedido | `mapa-de-caso-escritorio` — monta o grafo do caso e as lacunas antes de escrever |
| Pesquisa de jurisprudência/doutrina, leitura de documento pesado | subagentes `pesquisador-juridico` e `leitor-de-autos` — o mapa já delega a eles |
| Conferir a minuta contra o mapa, antes de timbrar | agente `revisor-adversarial` — o mapa também delega |
| Decidir **como** argumentar, depois que a tese já foi decidida | `retorica-juridica` |
| "já usei essa tese antes?", guardar tese ou precedente para depois | `acervo-de-teses` — o mapa consulta antes de pesquisar do zero |
| Documento final, timbrado, com print dos autos | `peticao-escritorio` |

**Precedência entre as duas gerações.** `mapa-de-caso-escritorio` e `peticao-escritorio` são as atuais. `mapa-de-caso` e `peticao-rg` ainda estão instaladas e reivindicam os mesmos pedidos — nos casos deste escritório, **as do escritório ganham sempre**; as antigas só valem em máquina onde as novas não existam. E `acervo-de-teses` substituiu `segundo-cerebro`: onde qualquer arquivo ainda disser `~/segundo-cerebro/`, leia como o acervo atual.

**A tabela acima é o núcleo verificado aqui — não a lista inteira.** O `mapa-de-caso` já referencia mais skills na sua própria máquina (`obsidian-litigation`, `whatsapp-transcricao`, `calculo-tjro`, `insights-gemini`, `prompt-injection-juridico`) que nunca foram auditadas nesta conversa — só confirmei que o `mapa-de-caso` assume que existem, não li o conteúdo delas. Se uma tocar num caso e o comportamento parecer errado, é sinal para investigar aquela skill, não para desconfiar do núcleo acima.

**Se a pasta da sessão tem PDFs de autos (inicial, contrato, decisão, laudo) e não parece projeto de código, é provável que seja um caso** — considere `mapa-de-caso` mesmo que o pedido não use a palavra "mapa" (ex.: "organiza esse processo", "o que temos de prova aqui", "monta a contestação").

**Ordem entre a skill de mapa e a de peça**: as duas reivindicam "redija a contestação", então vale a regra explícita — o mapa vem primeiro, sempre. A skill de peça formata o que já foi decidido; não decide o que escrever. (`peticao-escritorio` já recusa gerar com pendência aberta no mapa — o portão deixou de ser só instrução.) E não gere o documento final timbrado enquanto houver 🔴 aberto no mapa: peça bem diagramada em cima de lacuna não resolvida é pior que peça nenhuma, porque parece pronta para assinar.

## Quanto de esforço usar em cada caso

Não force multiagente/pipeline em todo caso — a maioria não precisa, e orquestração pesada sem necessidade só custa tempo e tokens sem ganho.

**`/loop` não serve para nada disso.** Ele some ao abrir conversa nova, sem aviso, e não retoma disparo perdido — serve para polling dentro de uma sessão, não para o que precisa sobreviver a você fechar o Claude. Prazo processual pede Routine. Detalhe e o caso específico que `/loop` desfaria: `references/delegacao.md`.

**Economize na coleta, nunca na conferência.** A assimetria decide tudo: token gasto à toa se perde uma vez; verificação pulada se perde o caso. Então corte a frente que não precisava existir — tese que o segundo cérebro já responde, delegação num caso de um fato só, segunda busca por capricho. Nunca corte a verificação do precedente, o mapa, nem o portão antes do documento final. E não corte instrução para poupar contexto: o texto das skills é ruído perto do que uma frente de pesquisa devolve.

**Antes de contar teses e documentos para decidir a escala, consulte o `segundo-cerebro`.** Ele existe para encolher essa conta: tese com nota lá, `verificado_em` dentro de 6 meses, não entra como "precisa de pesquisa" — já está resolvida, só falta ler. Só depois de descontar o que o acervo já responde, escale pelo que sobrou:

- **1 fato, 1 prova, 1 pedido, sem documento pesado e sem pesquisa pendente**: `mapa-de-caso` direto, sem delegar nada — cabe tudo numa análise só.
- **2 ou mais teses ainda sem nota verificada no segundo cérebro, documento pesado (laudo, contrato longo), ou precisa de pesquisa de jurisprudência/doutrina**: `mapa-de-caso` delega aos subagentes nomeados (`pesquisador-juridico`, `leitor-de-autos`) em paralelo — é o caso comum.
- **Muitas partes com posição própria a comparar** (litisconsórcio numeroso, concurso de credores em falência/recuperação/inventário) **ou muitos documentos**: aí sim vale perguntar se cabe um workflow de agentes maior para a etapa de leitura e pesquisa — o limiar exato de quando isso compensa está em `references/delegacao.md` do `mapa-de-caso`; não repito o número aqui para as duas referências não desalinharem com o tempo.

**Qual modelo em cada agente** está em `references/delegacao.md` — resumo: Sonnet nas frentes de pesquisa e leitura (os subagentes já vêm com isso no arquivo), Opus em quem consolida e em quem confere, Haiku quase nunca. E o recorte segura o custo mais que o modelo.

**Mesmo delegando a coleta, a comparação final é sempre sua.** Agentes em paralelo não conversam entre si — cruzar 8 posições numa única ordem de prioridade não vira 8 pareceres paralelos costurados depois; a leitura e a pesquisa paralelizam, o julgamento sobre como elas se relacionam não.

**Só a conversa principal toca o `segundo-cerebro`.** `pesquisador-juridico` e `leitor-de-autos` não têm acesso de leitura à pasta — eles verificam e devolvem o que encontram; quem lê o acervo antes de delegar e quem escreve nele depois (só com confirmação do usuário) é sempre a conversa principal, nunca um subagente isolado decidindo sozinho o que entra.

O grafo (mapa do caso) é sempre a etapa certa antes de redigir — isso não é "esforço extra", é o método. O que se calibra é só *quanto* delegar dentro dele, depois de checar o que o segundo cérebro já resolve.

## O que um agente decide, e o que só você decide

Não é o quanto o modelo parece confiante que abre a porta. Confiança é a variável mais fraca dessa decisão, por um motivo simples: é a única que ele consegue influenciar sozinho. O que abre a porta é **o tamanho do estrago se estiver errado**.

| Faixa | O que é | Quem decide |
|---|---|---|
| Reversível e contido | pesquisar jurisprudência, ler documento, montar cronologia, listar lacunas, conferir dispositivo | o agente decide e faz — errar custa refazer |
| Reversível e largo | qual tese sustentar, quais pedidos formular, o que impugnar, aceitar ou não um precedente contrário | o agente propõe, **você decide** — errar custa reescrever a peça |
| Difícil de reverter | protocolar · deixar precluir matéria do art. 337 §5º · não impugnar fato e deixá-lo incontroverso (art. 341) · abrir mão de prazo | **só você**, sempre |

A terceira faixa não é um limiar posto bem alto: é uma faixa que **não abre**. A diferença importa, porque limiar a gente afrouxa num dia corrido e faixa fechada não.

**Revise o mapa, não só a peça pronta.** No mapa o erro está nu — um fato sem prova, um `A` fazendo as vezes de `F`, um precedente sem link. Na peça redigida o mesmo erro já está vestido de prosa jurídica e custa três vezes mais para enxergar. Ler a matriz e a cronologia é mais barato *e* pega mais que ler o documento final.

## Regras que valem em qualquer sessão, com ou sem skill ativa

- **Nunca cite jurisprudência de memória** — número de processo, súmula, tema, relator. Só o que foi pesquisado nesta sessão ou já está com `verificado_em` no acervo. "Não localizado" é resposta completa — **dizendo onde se procurou e o que essa base cobre**. Zero resultado num índice parcial (período sincronizado, só 2º grau, só o que o boletim publica) quer dizer "nada nesta base", nunca "não existe no tribunal".
- **Aspas em trecho de julgado só depois de conferido no inteiro teor — e conferir inclui de quem é a frase.** Estar literalmente no acórdão não basta: o voto transcreve ementa de outro tribunal, traz voto vencido, reproduz alegação da parte. Trecho nessas condições não é palavra do tribunal que julgou.
- **Nunca publique conteúdo de um caso como artifact, página web ou link hospedado** — nome de parte, valor da causa e estratégia identificam o cliente, mesmo em link "privado".
- A decisão sobre teses, pedidos e protocolo é sempre sua — é a faixa que não abre, acima. Qualquer saída de IA é rascunho para revisão, nunca parecer pronto para assinar.
- **Ferramenta nova que vai tocar dado de caso (nome, fato, valor, estratégia) só entra depois de checar retenção, LGPD e subprocessador — do jeito que o JusRatio e os MCPs de tribunal já foram checados.** Não infira isso de post ou artigo de lançamento: o texto legal do próprio fornecedor é a fonte, e a ausência de menção à LGPD num DPA feito para GDPR/CCPA não é detalhe — é o documento não cobrir o seu caso. Decisão de exemplo, com o porquê por extenso: `references/delegacao.md` do `mapa-de-caso` (Jev/TypeSafe, 24/09).
