# Correção da skill `peticao-rg`

**Esta versão substitui a anterior.** A correção de 314→375 linhas que existia
aqui até 09/09 foi feita contra um `SKILL.md` que já não reflete o que está
instalado — a versão em uso real cresceu para 799 linhas por conta própria,
com conteúdo que esta correção teria apagado se copiada por cima (ver
`BASE-instalada-09-09.md`, a cópia exata do que estava instalado quando isso
foi descoberto). Nada do que segue foi testado num caso real, e isso está dito
abaixo com todas as letras.

**Não fica em `.claude/skills/`** de propósito: a skill real depende de
`scripts/` e `assets/template.docx`, que continuam só na máquina; uma cópia
dentro de `.claude/skills/` seria carregada pelo Claude Code e falharia ao
procurar o template.

## Como aplicar

Substitua **apenas** o `SKILL.md` da skill instalada. `scripts/`, `assets/` e
`references/` ficam intocados. **Antes de sobrescrever, confira se o que está
instalado agora ainda bate com `BASE-instalada-09-09.md`** — se divergiu de
novo nesse meio-tempo, este arquivo pode estar tão desatualizado quanto a
versão anterior estava.

```
diff ~/.claude/skills/peticao-rg/SKILL.md BASE-instalada-09-09.md   # deve dar vazio
cp SKILL.md ~/.claude/skills/peticao-rg/SKILL.md
```

## O que é isto, de verdade

Duas linhagens da mesma skill evoluíram em paralelo sem se falar: uma sessão
remota (que fez o desenho do portão — mapa antes de redigir, PARE antes de
gerar) e o uso real em casos de verdade (que fez o resto — timbre, blocos,
convenções extraídas de peças reais, e um **lint de citações que roda no
build e recusa a peça** se uma citação não bater com a ficha do precedente).
Isso aqui é a reconciliação: o portão, reaplicado do zero contra a versão de
799 linhas — não um `diff` antigo remendado por cima dela.

## O que o portão faz (inalterado em espírito desde a v1)

1. **Passo `0.` do Fluxo** — busca obrigatória pelo mapa do caso antes de
   escrever qualquer linha. *Não achou mapa? Pergunte* — nunca vira
   autorização para redigir direto.
2. **Checkpoint repetido** no passo `2.`, logo antes de montar o JSON.
3. **`## Quando vem de um mapa de caso`** — portão "PARE" cobrindo 🔴, ⏰, 🟡,
   e agora também `[PESQUISA NÃO REALIZADA]` e `[CONTRÁRIO NÃO RESOLVIDO]` —
   os dois marcadores que a linhagem de produção acrescentou ao
   `pesquisador-juridico` e que a v1 desta correção não conhecia. Decisão
   **item a item**, nunca um "pode gerar" global.
4. **Pendência de prazo não se resolve com marcador** — para item ⏰ só
   existem duas saídas: redigir agora, ou o advogado renunciar por escrito.

Uma peça a mais: o portão é anterior ao lint de citações do build, não
concorrente com ele. O lint confere a peça **já escrita** contra a ficha do
precedente; o portão impede que a peça comece a ser escrita com pendência
sem decisão do advogado. Os dois ficam.

## O que foi verificado nesta reconciliação, e como

Não rodei o build nem gerei DOCX desta vez — isso já tinha sido feito na v1,
contra o template real, e não há razão para achar que quebrou. O que **foi**
conferido, de forma mecânica, não por leitura:

- **Nenhum parágrafo da base de 799 linhas sumiu.** Script comparou os 21
  parágrafos substanciais do arquivo instalado contra o resultado da mesclagem
  — todos sobrevivem verbatim, exceto o único bloco que eu sei que toquei
  (o "Fluxo", passos 1-2). Zero perda silenciosa.
- **Diff final tem exatamente 2 hunks** — a inserção do passo `0` e a seção
  nova. Nada mais no arquivo foi reformatado ou tocado de passagem.
- YAML válido, descrição **idêntica** à instalada (não mexi nela — não achei
  problema nela desta vez).

## O que não foi verificado — e é mais do que da vez passada

- **Este merge específico nunca gerou um documento.** A v1 tinha um teste
  ponta a ponta (8 MB, 52 partes); esta reconciliação não repetiu isso contra
  a base nova, porque a base nova só apareceu nesta sessão.
- A renderização visual — timbre, rodapé, assinatura — segue sem conferência
  em qualquer ambiente além do Mac real.
- **O portão em si nunca rodou num caso real**, nem na v1 nem aqui.
- `mapa-de-caso` e os dois subagentes (`pesquisador-juridico`,
  `leitor-de-autos`) passaram pela mesma reconciliação, no mesmo commit desta
  branch — não numa pasta separada, porque não têm o problema de
  `scripts/`/`assets/` que exige manter o `peticao-rg` fora de
  `.claude/skills/`.
