# Delegação de pesquisa e leitura

Pesquisa boa depende de pergunta concreta. Por isso a delegação vem **depois** do inventário de nós: aí cada agente recebe a tese exata, o dispositivo, o tribunal e o que está em disputa — e não "pesquise sobre atraso de obra".

Dispare todos os agentes **numa única mensagem, em paralelo**. São independentes entre si; rodar em série só desperdiça tempo.

**Se os subagentes nomeados `pesquisador-juridico` e `leitor-de-autos` existirem** (`.claude/agents/`), use-os pelo nome — eles já têm a regra dura de citação e o escopo de ferramentas embutidos, então a delegação só precisa passar o concreto do caso (tese, dispositivo, documento), não reexplicar o método. Sem eles instalados, delegue a um agente genérico com as instruções completas de cada frente abaixo.

Só a conversa principal lê e escreve em `~/segundo-cerebro/` — nenhum subagente tem essa tarefa. `pesquisador-juridico` nem tem ferramenta de arquivo (só JusRatio e web); verifica e devolve, não consulta o acervo por conta própria.

## Antes de tudo — já existe isso no segundo cérebro?

Se a skill `segundo-cerebro` estiver instalada (`~/segundo-cerebro/`) e você ainda não conferiu o `indice.md` dela na Etapa 0, consulte agora, antes de delegar. Tese com nota lá já tem precedentes verificados com data — reconfirme se estiver com mais de 6 meses, mas não pesquise do zero o que já foi verificado.

Hoje o acervo só guarda nota de tese e de precedente (Frente 1 — jurisprudência). Para doutrina (Frente 3) e leitura de documento (Frente 4) a consulta raramente vai achar algo — não custa conferir, mas não espere cobertura. Sem `segundo-cerebro` instalado, todas as frentes abaixo partem do zero.

## Frente 1 — Jurisprudência (`pesquisador-juridico`, via JusRatio)

Um agente por tese estruturante. Teses acessórias podem ir juntas num agente só.

O que a delegação precisa conter:

- a **tese em uma frase**, com o dispositivo legal
- o **fato concreto** a que ela se aplica (é o que separa precedente aplicável de ementa genérica)
- a **contra-tese** que se espera — precedente contrário achado agora vale mais que surpresa na réplica
- o **tribunal de interesse**, quando houver
- instrução de devolver, para cada julgado: tribunal, órgão julgador, relator, data, número do processo, link e o trecho literal que interessa

Instruções operacionais para o agente:

- **Uma busca abrangente vale mais que várias fatiadas.** Peça `limit` de 20 a 30 numa chamada só; fragmentar degrada o resultado.
- Se for confirmar um julgado específico, **o número entra literal na query** ("REsp 1.234.567", "HC 843.649/RO") — a base tem busca exata por identificador, e sem o número no texto da consulta ele não dispara.
- Priorize autoridade **A** (vinculante) e **B** (precedente qualificado).
- Peça que sinalize precedente **superado** — tese boa que morreu é armadilha.
- **Cota mensal**: chamadas em janela de ~5 minutos contam como uma pesquisa. Não repita busca por capricho; se a cota estourar, o agente reporta e o mapa registra a tese como pendente.

## Frente 2 — Precedente local (TJRO)

Quando o caso corre ou vai correr no TJRO, o entendimento da câmara que vai julgar pesa mais que o de tribunal distante. Vale também mapear o relator, se já sorteado.

- Use o **MCP do TJRO** se estiver disponível na sessão.
- Se não estiver, use o JusRatio com `tribunais: ["TJRO"]`.
- **Diga no mapa qual via foi usada** — a cobertura das duas é diferente, e o advogado precisa saber se a busca local foi rasa.

Peça ao agente que separe o que é entendimento consolidado da câmara do que é decisão isolada, e que aponte divergência entre câmaras, se houver: divergência interna é argumento e é risco.

## Frente 3 — Doutrina (`pesquisador-juridico`, via web)

Para tese controvertida, nova, ou com pouca jurisprudência — onde o argumento precisa de autoridade acadêmica.

- Peça **autor, obra, edição e página** quando o agente conseguir; doutrina sem referência não se cita.
- Artigo de periódico jurídico, parecer publicado e manual de referência valem; post de blog e conteúdo de escritório valem como pista, não como fonte.
- Instrução explícita: **não invente citação doutrinária**. Autor e obra existentes com tese trocada é erro comum e difícil de flagrar.

## Frente 4 — Leitura de documento volumoso (`leitor-de-autos`)

Um agente por documento pesado (laudo extenso, contrato longo, peça da parte contrária com muitos anexos).

Peça de volta:

- estrutura do documento (o que tem em cada faixa de páginas)
- as **passagens literais** que importam, com número de página
- datas, valores e nomes que aparecem — para cruzar com a cronologia
- o que o documento **não** diz, quando a ausência for relevante (laudo que não conclui sobre nexo, contrato sem cláusula penal)

Instrução importante: o agente devolve o que está escrito, não o que deduz. Interpretação vem depois, no mapa, e sob a regra do nó `A`.

## Frente 5 — Verificação de dispositivo

Quando a tese depende de artigo específico e o texto exato importa (prazo, requisito, vedação), vale um agente que confirme a redação vigente do dispositivo e se houve alteração recente.

Artigo citado de cabeça é a alucinação mais discreta: o número está certo, o conteúdo não.

## Quando o caso for grande demais

Muitos documentos, muitos réus, muitos pedidos: pergunte ao usuário se ele quer rodar um **workflow de agentes** — leitura em paralelo de todos os documentos, depois pesquisa por tese, depois consolidação. Vale a pena a partir de umas dez frentes independentes; abaixo disso, subagentes em paralelo já dão conta e custam menos.

## Consolidando

Agentes em paralelo não conversam entre si — cada um só enxerga o próprio pedaço. Isso é seguro quando a tarefa é checável rápido (achou o julgado certo? leu o PDF certo?) e perigoso quando a coerência entre as frentes importa e ninguém olhou o conjunto. Antes de consolidar, é você — não os agentes — quem cruza os resultados:

- **Compare achados de frentes diferentes antes de virarem `PR` na mesma matriz.** Duas pesquisas sobre teses vizinhas podem trazer precedentes que se contradizem, ou um julgado que uma frente marcou como vigente e outra (ou a verificação de dispositivo) indica superado. Divergência entre agentes é sinal para checar, não para escolher o resultado que chegou primeiro.
- julgado vira nó `PR` **só** com identificação completa e link;
- o que não foi encontrado vira `[CARECE DE PRECEDENTE]`, não vira suposição;
- fato novo que apareceu na leitura de documento entra como `F` (documento comprova); leitura interpretativa entra como `A`;
- se um agente falhou ou a cota estourou, **registre isso no mapa** — pesquisa não feita não pode se parecer com pesquisa sem resultado.

## Quando uma frente volta errada

Uma frente voltou ruim — ementa genérica em vez de precedente aplicável, leitura que interpretou em vez de transcrever, cota estourada no meio. **Devolva só aquela frente.**

Reabrir o lote inteiro é o erro caro aqui, e ele não parece erro: as outras três frentes voltavam certas, são refeitas, e a nova versão vem *diferente*, não melhor — porque não havia nada errado nelas. Agora você tem quatro resultados para reconferir e três que podem falhar desta vez por motivo novo. Uma falha virou quatro incertezas. Feito duas vezes na mesma análise, o mapa não fecha nunca.

Visto de fora isso parece o agente falhando em série. Não é: é o caminho de volta destruindo trabalho que já estava bom.

Cinco coisas viajam com a devolução, e cada uma faz um serviço:

```
UNIDADE     Frente 1 — tese da prescrição intercorrente
VEREDITO    reprovado
MOTIVO      trouxe ementa genérica, não precedente com o mesmo fato
EVIDÊNCIA   os 3 acórdãos são de execução fiscal; nosso caso é execução de título extrajudicial
ESCOPO      refaça só esta tese; não toque nas outras frentes nem no que já entrou no mapa
```

A linha do **escopo** parece burocracia e não é. Sem ela a frente devolvida cresce: o agente reabre a busca, encontra outra tese interessante de passagem, traz junto — e a sua correção de uma frente virou material novo que ninguém pediu e que entra no mapa sem conferência.

**Ponha limite de tamanho na delegação, não só de assunto.** Pedido sem teto cresce sozinho: "cubra todas as hipóteses" e "uma por item" se multiplicam, e cada item costuma arrastar contexto próprio para fazer sentido. Diga quantos — quantos julgados, quantas páginas, quantas frentes — e o agente para onde você mandou parar. Sem teto, o custo não é proporcional à dificuldade da tarefa: é proporcional à imaginação de quem executa.

**Confira quem está fora há tempo demais.** Se uma frente demora muito mais que as outras da mesma rodada, o problema quase nunca é a frente ser mais difícil — é o recorte dela estar aberto demais. Interrompa e reformule em vez de esperar; esperar não conserta briefing.

**Pare na terceira tentativa.** Se a mesma frente falha três correções, o problema não está no agente: está na pergunta que você formulou — tese mal recortada, dispositivo errado, fato concreto que não é o que separa os precedentes. E o agente não enxerga a pergunta, só a resposta. Reformule a delegação, ou registre a tese como pendência de pesquisa no mapa e siga. Insistir uma quarta vez gasta cota e devolve a mesma coisa.
