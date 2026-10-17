# Correção da skill `peticao-rg`

**Terceira versão.** A produção continua evoluindo mais rápido do que qualquer
reconciliação pontual consegue acompanhar — 799 linhas em 09/09, 945 em 14/09,
cinco dias depois. `BASE-instalada-14-09.md` é a cópia exata do que estava
instalado quando isso foi capturado. Se você está lendo isto bem depois dessa
data, **confira antes de aplicar**: se o que está instalado não bater com
`BASE-instalada-14-09.md`, esta correção já está desatualizada do mesmo jeito
que a de 09/09 ficou.

**Não fica em `.claude/skills/`** de propósito: a skill real depende de
`scripts/` e `assets/template.docx`, que continuam só na máquina.

## Como aplicar

```
diff ~/.claude/skills/peticao-rg/SKILL.md BASE-instalada-14-09.md   # deve dar vazio
cp SKILL.md ~/.claude/skills/peticao-rg/SKILL.md
```

Se o `diff` não der vazio, pare — o arquivo instalado já mudou de novo desde
14/09, e aplicar por cima cegamente repete o erro que a v1 quase cometeu.

## O que a produção trouxe entre 09/09 e 14/09, que esta correção preserva

Nada disso é meu — vem de uso real, com incidentes datados no próprio arquivo.
Só preservei, não inventei nem simplifiquei:

- Roteamento por tribunal com MCPs próprios do TJRO, TRF1 (desde 11/09) e
  TCE-RO (desde 13/09), cada um com sintaxe de busca e teto de verificação
  diferentes
- O lint de citações (`lint_citacoes.py`) ganhou os campos novos que o
  `pesquisador-juridico` passou a produzir: `orgao_fonte`, `ratio_ou_dictum`,
  `fatos_relevantes`, `overruling_status`
- Medição real (14/09): 15 de 24 processos que o cadastro do TJRO classificou
  na "3ª Câmara Cível" foram julgados por outra câmara — daí a exigência de
  `orgao_fonte: "fecho"` para citar câmara do TJRO

## O que esta correção acrescenta de novo, desde a v2

O portão ("mapa antes de redigir") foi **reaplicado do zero** contra a base de
945 linhas — não é o diff de 09/09 remendado. E passou a cobrir o que a
produção acrescentou desde então: precedente que o mapa marcou "aplica por
extensão" entra na peça dizendo que é extensão, fora das aspas; `PR` marcado
"distingue" de um fato do caso não entra como se sustentasse a tese.

## Verificado nesta reconciliação

- Todos os 24 parágrafos substanciais da base de 945 linhas sobrevivem
  verbatim no resultado, exceto o único bloco deliberadamente tocado (Fluxo,
  passos 1-2) — conferido por script, não por leitura
- YAML válido, descrição inalterada (não achei problema nela desta vez)

## O que não foi verificado — igual às duas vezes anteriores

- Este merge específico nunca gerou um documento nem rodou o `lint_citacoes.py`
- O portão em si nunca rodou num caso real
- Não avaliei se `effort: high` (subido no `pesquisador-juridico` nesta
  rodada, por causa do roteamento multi-tribunal) é o nível certo — é
  julgamento sobre a complexidade que o agente ganhou, não medição
