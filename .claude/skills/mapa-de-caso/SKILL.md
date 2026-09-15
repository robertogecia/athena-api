---
name: mapa-de-caso
description: >-
  Lê os autos (PDFs e documentos de uma pasta do caso), monta o mapa do caso — a
  cadeia pedido ← tese ← fato ← prova, com partes, contra-teses e prazos — e
  diagnostica as lacunas antes da redação — alegação sem prova, pedido
  descoberto, fato não impugnado, contra-tese sem resposta, contradição de datas
  e preclusão iminente. Delega a subagentes em paralelo a pesquisa de
  jurisprudência (JusRatio), de precedente local (MCPs do TJRO, do TRF1 e do TCE-RO) e de doutrina na web.
  Use SEMPRE antes de redigir peça (inicial, contestação, réplica, recurso,
  parecer) quando o caso tiver mais de um fato, prova ou pedido — mesmo que o
  pedido do usuário seja direto, do tipo redija a contestação, monte o mapa
  primeiro e só então redija. Use também quando o usuário mandar analisar autos,
  organizar caso, montar cronologia, avaliar viabilidade de ação ou achar o
  ponto fraco de uma tese. Não use para formatar ou timbrar texto já pronto
  (isso é peticao-rg) nem para revisar um trecho isolado.
---

# Mapa de Caso

Uma peça convence quando cada pedido desce, sem degrau quebrado, até uma prova nos autos: **pedido ← tese ← fato ← prova**. O mapa torna essa cadeia visível enquanto ainda dá para juntar documento, pesquisar precedente ou trocar de estratégia.

O mapa é ferramenta interna. Ele não vai para os autos — ele decide o que vai.

## Roteiro

```
[ ] 0. Reconhecer os autos: indexar a pasta, ler o essencial, montar o índice de peças
[ ] 1. Testar a via: o pedido que o cliente quer é mesmo o melhor remédio?
[ ] 2. Inventariar nós (F, A, PV, T, CT, PD, PR) com atributos
[ ] 3. Ligar os nós
[ ] 4. Delegar pesquisa a subagentes em paralelo
[ ] 5. Rodar o diagnóstico de lacunas
[ ] 6. Entregar: matriz + cronologia + lacunas (+ diagrama se pedido)
```

Não pergunte antes de começar. Infira a peça e o polo do contexto e declare a premissa em uma linha no topo do mapa — *"Peça: contestação · Cliente no polo passivo · Juízo: 3ª Vara Cível de Porto Velho/TJRO — corrija se estiver errado"*. Só pergunte se peça e polo forem ambos indetermináveis.

## Etapa 0 — Reconhecer os autos

O caso normalmente chega como pasta de arquivos, não como narrativa digitada. Comece por ela.

1. **Liste a pasta** e identifique cada arquivo pelo que ele é: inicial, contestação, contrato, laudo, decisão, comprovante, print. Nomes de arquivo mentem — abra e confira.
2. **Leia integralmente** o que decide o caso: a peça da parte contrária, o contrato ou título, o laudo, a decisão recorrida. Esses não admitem amostragem.
3. **Amostragem declarada** no volume repetitivo (extratos, planilhas, e-mails em série): diga no mapa o que leu por amostra e o que ficou de fora, para o advogado saber onde a análise é rasa.
4. **Monte o índice de peças** com localização — é dele que sai a citação de cada prova:

| # | Documento | Arquivo | Fls./págs. | O que prova |
|---|-----------|---------|-----------|-------------|

Se um PDF for grande demais para ler direto, delegue a leitura a um subagente (Etapa 4) pedindo o resumo estruturado e as passagens literais que interessam, com página.

Documento em DOCX, XLSX, PPTX, RTF ou EPUB, ou PDF que o `Read` não extrai limpo: se o CLI [`anydoc`](https://github.com/firecrawl/anydoc) estiver instalado, use-o (`Bash`) para converter em Markdown antes de ler — processa local, nada sai da máquina, e cobre formato que a leitura direta não pega. Sem ele, leia o que der e registre no índice o que não abriu.

Export do WhatsApp com áudio ou vídeo (audiência, depoimento, nota de voz do cliente): transcrever primeiro com a skill `whatsapp-transcricao` (100% local) e tratar a transcrição como documento do caso, com origem citada.

**Peça digital vinda de terceiro (parte adversa, perito, cartório) em PDF/DOCX/HTML:** a varredura de prompt injection **não roda mais sozinha** — o usuário desativou o disparo automático de propósito. Quando a pasta tiver peça de origem externa e você for resumi-la ou triá-la, **ofereça** a varredura numa linha (`skill prompt-injection-juridico`, ou `python3 ~/skills/prompt-injection-juridico/scripts/scan.py "<arquivo>"`) e siga o trabalho — **não execute sem ele pedir**. É onde o risco de fato mora (instrução escondida na peça do adversário para manipular o resumo), mas a decisão de gastar esse passo é dele, não sua.

**Toda prova no mapa cita origem**: `PV3 · Contrato de empreitada · doc-02.pdf, fls. 12-18`. Prova sem localização é prova que você não vai achar na hora da audiência.

5. **Se a skill `segundo-cerebro` estiver instalada, dê uma olhada no `indice.md` dela agora** — antes de inventariar os nós, não só na hora de delegar. Informa de cara se alguma tese do caso já está resolvida (nota com `verificado_em` dentro de 6 meses), o que muda quanto esforço o caso todo vai pedir. A Etapa 4 não precisa reconsultar o que já foi visto aqui — só delegar o que ficou de fora.

6. **Caso que vive no vault Obsidian** (`01 - Projetos/`): siga também a skill `obsidian-litigation` — ela rege as convenções do vault (nomenclatura, fichas, onde salvar o mapa e as minutas) e a disciplina dos MCPs jurídicos. O mapa continua sendo o diagnóstico; ela é a camada de vault e ferramentas dentro dele.

7. **Consulte a memória nativa do Claude Code para este caso especificamente — não só o `indice.md` do segundo-cérebro.** `MEMORY.md` traz uma linha-resumo por caso; ela é ponteiro, não o conteúdo. Se já existir linha para este caso, **abra o arquivo inteiro** que ela referencia antes de tratar qualquer achado novo (documento reencontrado, áudio recatalogado, fato reconfirmado) como novidade ou como motivo de alarme para o advogado. O que parece descoberta pode já estar mapeado, com mais profundidade, numa apuração anterior — e resumo de uma linha não é substituto de abrir o arquivo. Erro real, 06/09/2026: uma sessão recatalogou meses de áudio de WhatsApp e "descobriu" por transcrição uma fraude à execução que já estava documentada, com mais rigor (12 agentes, apuração dedicada), numa memória nativa escrita três semanas antes — cuja linha de resumo em `MEMORY.md` já apontava exatamente para aquilo, e não foi aberta antes de soar o alarme.

## Etapa 1 — Testar a via

Antes de mapear, pergunte-se se o remédio pedido é o melhor para o cliente. Esta etapa existe porque é o erro mais caro e o mais fácil de não enxergar: um mapa impecável de uma estratégia errada continua sendo uma estratégia errada.

- Resolver o contrato ou exigir o cumprimento? (se o bem valorizou, devolver o preço pode arruinar o cliente)
- Ação própria ou incidente no processo existente?
- Vale o custo, o tempo e o risco de sucumbência?
- Há prazo mais vantajoso, via administrativa ou acordo em aberto?

Duas ou três linhas bastam. Se a via pedida for pior que a alternativa, **diga isso primeiro, antes do mapa** — e mapeie as duas se a diferença for relevante.

## Etapa 2 — Inventariar os nós

| Prefixo | Tipo | O que entra |
|---------|------|-------------|
| `F` | Fato | Evento que **alguém afirmou** ou que **documento comprova**. Um fato = um evento |
| `A` | **Assunção** | O que **você** derivou: data calculada, cláusula presumida, enquadramento jurídico suposto, fato provável |
| `PV` | Prova | Documento, testemunha, perícia — com arquivo e fls. |
| `T` | Tese | A regra aplicada ao fato, com o dispositivo |
| `CT` | Contra-tese | Argumento da parte contrária, real ou previsível |
| `PD` | Pedido | Cada pedido, separadamente |
| `PR` | Precedente/norma | Só o **verificado** nesta sessão (Etapa 4) |

Partes e envolvidos ficam numa tabela à parte, fora do grafo — elas qualificam os nós, não se ligam a eles.

### A regra do nó `A` — a mais importante deste arquivo

**Nada que o usuário não tenha afirmado, e nenhum documento não comprove, entra como `F`.**

Data que você calculou, cláusula que você pressupôs existir, "o cliente é consumidor", "a carga foi transportada com as cautelas devidas" — tudo isso é `A`, não `F`. Assunções:

- ficam **fora da cronologia** e numa seção própria "Assunções a confirmar";
- **nunca recebem prova**: ligar `PV → prova → A` é designar testemunha para um fato que ainda não existe, ou seja, fabricar caso;
- contaminam para baixo: tese que depende de `A` não passa de 🟡.

Isso importa porque a seção "Dos Fatos" da peça sai da cronologia. Um `A` disfarçado de `F` vira alegação de fato numa petição assinada por você.

### Atributos que mudam o diagnóstico

Nó burro produz diagnóstico burro. Anote em cada nó:

- **`F.status`** — *incontroverso* (a parte contrária admite ou não impugnou) · *controvertido* · *alegado pela outra parte* · *notório*. Fato incontroverso e notório **dispensam prova** (art. 374 CPC) e não podem ser marcados como lacuna.
- **`F.ônus`** — de quem é a prova (art. 373): constitutivo é do autor; impeditivo, modificativo e extintivo são do réu. Sem isso a severidade é chute. Anote também quando couber inversão (CDC art. 6º, VIII) ou distribuição dinâmica (art. 373, §1º).
- **`PV.força`** — *idônea* (documento assinado, perícia judicial) · *frágil* (unilateral, sem data, testemunha suspeita ou empregada, print sem ata notarial).
- **`PD.prazo`** — decadência, prescrição, prazo recursal. Toda conta de prazo declara a data-base usada e marca a premissa como `A` até você confirmar.

## Etapa 3 — Ligar os nós

| Aresta | Significado |
|--------|-------------|
| `PV -->\|prova\| F` | Prova idônea demonstra o fato |
| `PV -.->\|prova frágil\| F` | Prova existe mas é atacável |
| `F -->\|sustenta\| T` | O fato atrai a tese |
| `T -->\|fundamenta\| PD` | A tese justifica o pedido |
| `PR -->\|reforça\| T` | Precedente verificado dá autoridade |
| `CT -.->\|ataca\| T` | Contra-tese mira a tese |
| `T -->\|responde\| CT` | Tese que neutraliza a contra-tese |
| `F1 -.-\|contradiz\| F2` | Versões incompatíveis, sobretudo de data |

Tipar o ataque muda o parágrafo que você escreve: a contra-tese **nega a prova** ("o documento é falso"), **nega a conclusão** ("mesmo assim não há dano") ou **nega o enquadramento** ("esse artigo não incide aqui")? Anote qual.

Percorra cada `PD` de cima para baixo. Se a descida não chega a um `PV`, o pedido está descoberto.

## Etapa 4 — Delegar a pesquisa

Dispare os subagentes **em paralelo, numa única mensagem**, depois que o inventário estiver pronto — assim cada um recebe a tese concreta a pesquisar, não uma pergunta vaga. Detalhes de como redigir cada delegação: `references/delegacao.md`.

Se um subagente voltar com `[PESQUISA NÃO REALIZADA — motivo]`, trate como pesquisa **pendente**, não como ausência de precedente: a tese fica 🟡/🔴 por falta de verificação e o mapa diz o motivo. Ausência de pesquisa nunca vira "não localizado".

Se voltar com `[CONTRÁRIO NÃO RESOLVIDO — ...]`, a tese fica 🔴 até alguém ler o voto e resolver na ficha (`limites`/`sustenta`). Tirar o precedente da peça não resolve: ele continua vivo para a parte contrária e para o relator. E ao redigir, a citação segue o `sustenta` **e** o `limites` da ficha — se o julgado condiciona ("mediante fraude"), a peça condiciona; caso sem a condição não cita o julgado como se tivesse.

Frentes típicas:

- **Jurisprudência (JusRatio)** — STJ, STF e tribunais sem MCP próprio; uma busca abrangente por tese, não várias fatiadas.
- **Precedente local** — quando o caso corre ou vai correr num tribunal específico, o entendimento do órgão que vai julgar vale mais que o de tribunal distante. **Tribunal com MCP próprio (hoje TJRO, TRF1 e TCE-RO) é pesquisado só nele** (decisão do advogado, 10/09/2026, estendida em 11/09 e 13/09/2026); qual motor atende qual tribunal é a tabela do `pesquisador-juridico`, chaveada pelo número CNJ ou pela matéria (contas → TCE-RO) — não a repita aqui. Sem o MCP na sessão, aquela frente fica pendente e o mapa diz o motivo — nunca é suprida pelo JusRatio.
- **Doutrina (web)** — para tese controvertida ou pouco julgada, onde o argumento precisa de autoridade acadêmica.
- **Leitura de documento volumoso** — um agente por PDF pesado, devolvendo estrutura e passagens literais com página.

**A regra dura da citação:** só entra no mapa como `PR` o que voltou de uma pesquisa desta sessão, como **ficha de precedente** do `pesquisador-juridico` (tribunal, órgão e relator lidos do texto, data de julgamento, número, id do documento, link, trecho literal, `verificacao`). Nada de memória. A ficha vai inteira para `precedentes` do JSON da `peticao-rg`, que recusa gerar a peça com citação sem ficha. Um número de processo pode ter vários julgados (original, embargos, voto vencido): a decisão se identifica por número + data + id, nunca só pelo número.

- **Acórdão de turma**: só se veio da pesquisa. Sem exceção.
- **Súmula, tema repetitivo, repercussão geral e artigo de lei**: pode citar, sempre marcando *conferir vigência* — súmula é cancelada e lei é revogada.
- **Não encontrou?** "Não localizado" é resposta legítima e completa. Escreva `[CARECE DE PRECEDENTE]` e siga. Nunca preencha o buraco com o que parece existir.
- **Verifique o dispositivo antes de citar**: artigo lembrado de cabeça é a alucinação mais discreta que existe, porque o número está certo e o conteúdo não.
- **Brainstorming da skill `insights-gemini` nunca vira `PR`** — é saída não verificada, mesmo quando parece pesquisa com fontes; serve no máximo para sugerir onde pesquisar.

Julgado inventado em peça rende multa de 1% a 10% do valor da causa (CPC arts. 77, 80 e 81) e ofício à OAB — já aconteceu no TST, no TJPR, no TJSC e na Justiça Federal. É o único erro deste roteiro que custa dinheiro na hora.

**Ligar `PR` a `T` é um passo de comparação, não de colagem.** A ficha traz `fatos_relevantes`, de 2 a 4 fatos materiais de que a ratio depende. Cruze-os com os nós `F` do caso, um a um, e escreva no mapa uma das três conclusões:

- **aplica** — os fatos materiais estão presentes no caso; o precedente sustenta a tese direto;
- **aplica por extensão** — a ratio é geral, mas o caso concreto do precedente é outro (ex.: tese enunciada para extinção em 1º grau, usada no plano recursal). Legítimo, e a peça tem de dizer que é extensão, em parágrafo próprio, fora das aspas;
- **distingue** — falta um fato material. Aí o precedente não sustenta, e se for adverso é você quem escreve a distinção antes que a parte contrária a negue.

Isso é o que nenhum agente de pesquisa pode fazer por você: ele não conhece os `F` do caso. Dois erros reais nasceram exatamente dessa etapa faltando — precedente de nulidade por fraude comprovada usado em caso de simples falta de prova (categorias diferentes, validade contra existência), e tese de repetitivo restrita a execução fiscal generalizada para execução civil.

**`ratio_ou_dictum` muda o peso.** Trecho que a ficha marca como `dictum`, ou como `indeterminado` porque só a ementa foi lida, não sustenta tese sozinho: ou se lê o inteiro teor, ou o `PR` entra como reforço, nunca como fundamento principal. Dictum citado como ratio é o que a parte contrária desmonta em uma linha.

## Etapa 5 — Diagnosticar lacunas

| # | Lacuna | Como detectar | Severidade |
|---|--------|---------------|------------|
| 1 | **Alegação órfã** | `F` controvertido, cujo ônus é do cliente, sem `prova` chegando | 🔴 se essencial · 🟡 se acessório · **não é lacuna** se incontroverso, notório ou de ônus alheio |
| 2 | **Pedido descoberto** | `PD` cuja cadeia não desce até um `PV` | 🔴 |
| 3 | **Assunção estruturante** | `A` da qual depende tese ou pedido | 🔴 até virar `F` ou cair |
| 4 | **Tese nua** | `T` sem norma conferida nem precedente verificado | 🟡 |
| 5 | **Contradição** | `F -.- F` incompatíveis, sobretudo datas | 🔴 na narrativa do cliente · **trunfo** na da parte contrária, destaque |
| 6 | **Contra-tese aberta** | `CT` sem `responde` | 🟡 a 🔴 conforme a gravidade |
| 7 | **Prova frágil ou solta** | `PV` unilateral/suspeita, ou que não prova fato nenhum alegado | 🟡 |
| 8 | **Preclusão iminente** | Matéria que só pode ser alegada agora | 🔴 — ver `references/checklists-cpc.md` |
| 9 | **Precedente sem identidade fática** | `PR` ligado a `T` sem que os `fatos_relevantes` da ficha tenham sido cruzados com os `F` do caso, ou cruzamento que resultou em "distingue" | 🟡 se é reforço · 🔴 se é o único `PR` da tese |
| 10 | **Contrário não resolvido** | agente devolveu `[CONTRÁRIO NÃO RESOLVIDO]`, ou a ficha traz precedente adverso sem distinção escrita | 🔴 — tirar da peça não resolve, o julgado continua vivo para a parte contrária e para o relator |

Fechado o checklist, levante os olhos dos autos e pergunte duas coisas — elas não saem de nenhuma lista, e é onde costuma estar o que vira o jogo:

**O que existe fora dos autos?** Lacuna probatória raramente se resolve só com o que já está na pasta. Certidão de órgão público (habite-se, alvará, licença, ART/RRT no CREA, boletim de ocorrência), ata notarial para congelar estado de fato que o tempo apaga, exibição de documento em poder da outra parte ou de terceiro (arts. 396 e ss.), ofício a banco ou operadora, prova emprestada de outro processo. Documento oficial contra a tese adversária vale mais que três testemunhas favoráveis — e converte lacuna em diligência, que é ação, não fraqueza.

**Quanto vale isso, de verdade?** Feche com uma leitura econômica em duas ou três linhas: o cenário provável em números, a faixa de acordo razoável, e o custo de litigar até o fim. O advogado precisa disso para conversar com o cliente antes da peça — e às vezes o mapa mostra que o melhor resultado possível é pior que um acordo que já está na mesa. Valor que depende de atualização monetária ou cálculo de cumprimento de sentença no TJRO: gerar com a skill `calculo-tjro` (Calculadora Judicial oficial), não estimar.

**A regra do verde.** 🟢 exige as quatro: cadeia fecha em prova existente, dispositivo conferido no texto da lei, precedente verificado nesta sessão, e cruzamento de fatos feito (o `PR` "aplica" ou "aplica por extensão", com a extensão declarada). Faltando qualquer uma, no máximo 🟡. Tese que depende de `A` ou que tem 🔴 na cadeia **herda o 🔴** — nunca aparece como 🟡 ou 🟢.

E o rodapé obrigatório da matriz: *"🟢 significa 'sem lacuna detectada pelo checklist', não 'pronto para protocolar'."*

Rode também o checklist processual da peça em questão — requisitos da inicial, impugnação especificada e preliminares da contestação, matérias que precluem: `references/checklists-cpc.md`.

Não invente fato nem suponha prova para fechar lacuna. Lacuna aberta é o produto desta skill, não uma falha dela. Às vezes o mapa mostra que o caso precisa de mais prova antes de valer o ajuizamento — dizer isso é o serviço.

## Etapa 6 — Entregar

```markdown
# Mapa do Caso — [identificação]
**Premissa:** [peça · polo do cliente · juízo] — corrija se estiver errado

## 1. Resumo
[3 a 6 linhas: quem, contra quem, o quê, em que fase]

## 2. Via escolhida
[Etapa 1: o remédio pedido é o melhor? alternativa, se houver]

## 3. Índice de peças
| # | Documento | Arquivo | Fls. | O que prova |

## 4. Cronologia
| Data | Fato | Prova (arquivo, fls.) | Status |
[só `F` — assunções não entram aqui]

## 5. Matriz de amarração
| Pedido | Tese | Fato(s) | Prova(s) | Ônus | Precedente | Status |
*🟢 = sem lacuna detectada pelo checklist, não "pronto para protocolar".*

## 6. Assunções a confirmar
| ID | O que assumi | Por quê | Como confirmar |

## 7. Lacunas e ações
### 🔴 Antes de protocolar
- [lacuna] → [ação concreta]
### 🟡 Atenção
### ⏰ Prazo e preclusão
### 🔍 Diligências fora dos autos
- [certidão, ata notarial, exibição, ofício] → [o que provaria]

## 8. Leitura econômica
[cenário provável em números · faixa de acordo · custo de litigar]

## 9. Próximo passo
```

**A matriz é a fonte de verdade.** Ela sai sempre. O diagrama é derivado e opcional: gere quando o usuário pedir ou quando houver mais de duas partes ou mais de quatro pedidos — casos em que o desenho realmente ajuda a enxergar. Convenções em `references/diagrama.md`.

Se gerar o diagrama, ele tem que **fechar com a matriz**: todo `PD` da matriz aparece como nó, toda cor bate com o Status, nenhum nó fica sem classe, e nenhum pedido é omitido "para não poluir" — se não couber, divida por pedido. Um mapa que se contradiz é pior que nenhum mapa.

Antes de entregar, releia o que montou e confira: cada ID tem um enunciado só (a mesma tese não pode aparecer com três redações), a cronologia só cita fatos que existem no inventário, e o Status da matriz reflete o diagnóstico da Etapa 5.

Entregue na conversa e salve como `.md` na pasta do caso.

## Do mapa à peça

Se o usuário já pediu a peça, não pare para perguntar: entregue o mapa e siga direto para a redação — a menos que haja 🔴 que impeça, e aí diga qual e por quê.

- **Dos Fatos** = a cronologia em prosa, na ordem das datas, cada fato com sua prova citada por fls.
- **Do Direito** = um bloco por pedido, subindo a cadeia: tese, aplicação ao fato, prova, precedente verificado.
- **Contra-teses** viram refutação preventiva; na contestação, cada fato da inicial precisa de impugnação expressa (art. 341).
- **Pedidos** = os `PD`, em ordem de dependência lógica.

O mapa é diagnóstico, não índice de parágrafos — se a peça pedir outra ordem ou outro fôlego, escreva melhor e ignore a estrutura. Tese ou pedido que **você** sugeriu, e o advogado ainda não adotou, vai marcado **(sugerido — validar)**.

Para o documento final timbrado em DOCX/PDF, use a skill `peticao-rg`.

Se a skill `segundo-cerebro` estiver instalada e a peça já tiver sido redigida (não antes — só o que de fato foi usado entra lá), ofereça depositar as teses e os precedentes verificados deste caso. É o que faz o próximo caso sobre o mesmo tema começar sem pesquisar do zero.

## Sigilo

O mapa reúne partes identificadas, valores, provas e a lista das fraquezas do cliente. É o arquivo mais sensível do caso.

**Nunca publique o mapa como artifact, página HTML ou qualquer link hospedado**, mesmo privado — um link compartilhado por engano é quebra de sigilo profissional (CED/OAB art. 36), e em processo sob segredo de justiça (CPC art. 189) é violação adicional. Se o usuário insistir, produza versão anonimizada (partes por iniciais, valores por faixa, sem número de processo) e diga por escrito o que foi removido.

Não anexe o mapa a e-mail para o cliente nem deposite em pasta compartilhada. E não junte aos autos.

## Limites

A decisão sobre teses, pedidos e protocolo é do advogado, que responde pessoalmente pelo que protocola. A norma aplicável é a **Recomendação CFOAB nº 001/2024** (independência técnica, sigilo, verificação humana, comunicação ao cliente sobre uso de IA) e o Código de Ética da OAB — a Resolução CNJ 615/2025 rege o uso de IA **pelo Judiciário** e não alcança escritórios.

Apontar prova a produzir é o trabalho. Sugerir o que uma testemunha "deve dizer" é crime (CP art. 343) — a lista de lacunas serve para buscar prova, nunca para construí-la.

## Referências

- `references/delegacao.md` — como redigir cada delegação de pesquisa e leitura
- `references/checklists-cpc.md` — inicial, contestação, recurso e o que preclui
- `references/diagrama.md` — convenções de Mermaid quando o diagrama for gerado
