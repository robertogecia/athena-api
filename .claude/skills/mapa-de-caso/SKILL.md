---
name: mapa-de-caso
description: >-
  Lê os autos (PDFs de uma pasta do caso), monta o mapa do caso — a cadeia
  pedido ← tese ← fato ← prova, com partes, contra-teses e prazos — e
  diagnostica as lacunas antes da redação: alegação sem prova, pedido
  descoberto, fato não impugnado, contradição de datas, preclusão iminente.
  Delega a subagentes a pesquisa de jurisprudência (JusRatio), de precedente
  local (TJRO) e de doutrina na web. Use SEMPRE antes de redigir peça
  contenciosa — inicial, contestação, réplica, reconvenção, impugnação, parecer,
  alegações finais e recurso de qualquer tipo (apelação, agravo, embargos);
  lista exemplificativa, vale para qualquer peça que dependa de fato, prova e
  tese — mesmo que o pedido seja direto, do tipo redija a contestação: monte o
  mapa primeiro e só então redija. Use também para analisar autos, organizar
  caso, montar cronologia ou achar o ponto fraco de uma tese. Não use para
  formatar ou timbrar texto pronto, nem para gerar o DOCX/PDF de peça já
  redigida (isso é peticao-rg), nem para revisar trecho isolado.
---

# Mapa de Caso

Uma peça convence quando cada pedido desce, sem degrau quebrado, até uma prova nos autos: **pedido ← tese ← fato ← prova**. O mapa torna essa cadeia visível enquanto ainda dá para juntar documento, pesquisar precedente ou trocar de estratégia.

O mapa é ferramenta interna. Ele não vai para os autos — ele decide o que vai.

## O que reprova este mapa

Antes do roteiro, a condição — porque conferência escrita depois do trabalho vira carimbo. Sem algo que possa **reprovar** o mapa enquanto ninguém está olhando, não existe conferência: existe roteiro.

Estas seis reprovam, e nenhuma delas exige julgar mérito. São conferíveis olhando a estrutura:

```
REPROVA   F controvertido, de ônus do cliente, sem PV chegando nele
REPROVA   PD cuja cadeia não desce até um PV
REPROVA   T ou PD que depende de um nó A
REPROVA   PR sem tribunal, órgão, relator, data, número e link
REPROVA   matéria do art. 337 que preclui nesta peça e ficou sem decisão
REPROVA   contradição de datas na narrativa do cliente
```

```
NÃO REPROVA   "o mapa parece completo"
NÃO REPROVA   "não encontrei problemas"
NÃO REPROVA   nenhum erro apareceu na leitura
```

A última é a que pega gente cuidadosa: **ausência de erro não é prova de correção.** Quem não achou lacuna pode não ter procurado — e o custo do engano fica com o cliente, não com quem leu.

O diagnóstico completo, com as oito lacunas e as severidades, está na Etapa 5. Isto aqui é a condição, e ela vem antes de propósito.

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

**Saída curta.** Se, ao abrir os autos, o caso tiver mesmo um fato, uma prova e um pedido — cobrança de título único, rito simples sem controvérsia fática —, não monte o aparato inteiro: entregue a matriz de amarração, o prazo e as lacunas em poucas linhas e siga para a redação. Isso se decide **depois** de ler, nunca antes: só olhando os autos dá para saber se o caso é simples, e é por isso que não é condição de gatilho da skill.

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

**Toda prova no mapa cita origem**: `PV3 · Contrato de empreitada · doc-02.pdf, fls. 12-18`. Prova sem localização é prova que você não vai achar na hora da audiência.

5. **Se a skill `segundo-cerebro` estiver instalada, dê uma olhada no `indice.md` dela agora** — antes de inventariar os nós, não só na hora de delegar. Informa de cara se alguma tese do caso já está resolvida (nota com `verificado_em` dentro de 6 meses), o que muda quanto esforço o caso todo vai pedir. A Etapa 4 não precisa reconsultar o que já foi visto aqui — só delegar o que ficou de fora.

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

Frentes típicas:

- **Jurisprudência (JusRatio)** — uma busca abrangente por tese, não várias fatiadas.
- **Precedente local** — quando o caso corre ou vai correr no TJRO, o entendimento da câmara que vai julgar vale mais que o de tribunal distante. Use o MCP do TJRO se estiver disponível na sessão; se não estiver, use o JusRatio filtrando por `tribunais: ["TJRO"]` e diga no mapa qual via usou.
- **Doutrina (web)** — para tese controvertida ou pouco julgada, onde o argumento precisa de autoridade acadêmica.
- **Leitura de documento volumoso** — um agente por PDF pesado, devolvendo estrutura e passagens literais com página.

**A regra dura da citação:** só entra no mapa como `PR` o que voltou de uma pesquisa desta sessão, com identificação completa (tribunal, órgão, relator, data, número) e link. Nada de memória.

- **Acórdão de turma**: só se veio da pesquisa. Sem exceção.
- **Súmula, tema repetitivo, repercussão geral e artigo de lei**: pode citar, sempre marcando *conferir vigência* — súmula é cancelada e lei é revogada.
- **Não encontrou?** "Não localizado" é resposta legítima e completa. Escreva `[CARECE DE PRECEDENTE]` e siga. Nunca preencha o buraco com o que parece existir.
- **Verifique o dispositivo antes de citar**: artigo lembrado de cabeça é a alucinação mais discreta que existe, porque o número está certo e o conteúdo não.

Julgado inventado em peça rende multa de 1% a 10% do valor da causa (CPC arts. 77, 80 e 81) e ofício à OAB — já aconteceu no TST, no TJPR, no TJSC e na Justiça Federal. É o único erro deste roteiro que custa dinheiro na hora.

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

Fechado o checklist, levante os olhos dos autos e pergunte duas coisas — elas não saem de nenhuma lista, e é onde costuma estar o que vira o jogo:

**O que existe fora dos autos?** Lacuna probatória raramente se resolve só com o que já está na pasta. Certidão de órgão público (habite-se, alvará, licença, ART/RRT no CREA, boletim de ocorrência), ata notarial para congelar estado de fato que o tempo apaga, exibição de documento em poder da outra parte ou de terceiro (arts. 396 e ss.), ofício a banco ou operadora, prova emprestada de outro processo. Documento oficial contra a tese adversária vale mais que três testemunhas favoráveis — e converte lacuna em diligência, que é ação, não fraqueza.

**Quanto vale isso, de verdade?** Feche com uma leitura econômica em duas ou três linhas: o cenário provável em números, a faixa de acordo razoável, e o custo de litigar até o fim. O advogado precisa disso para conversar com o cliente antes da peça — e às vezes o mapa mostra que o melhor resultado possível é pior que um acordo que já está na mesa.

**A regra do verde.** 🟢 exige as três: cadeia fecha em prova existente, dispositivo conferido no texto da lei, e precedente verificado nesta sessão. Faltando qualquer uma, no máximo 🟡. Tese que depende de `A` ou que tem 🔴 na cadeia **herda o 🔴** — nunca aparece como 🟡 ou 🟢.

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
