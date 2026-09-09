# Correção da skill `peticao-rg`

Cópia versionada da `SKILL.md` corrigida da `peticao-rg`, para não depender do
histórico de uma conversa. **Não fica em `.claude/skills/`** de propósito: a skill
real depende de `scripts/` e `assets/template.docx`, que continuam só na máquina;
uma cópia dentro de `.claude/skills/` seria carregada pelo Claude Code e falharia
ao procurar o template.

## Como aplicar

Substitua **apenas** o `SKILL.md` da skill instalada. `scripts/`, `assets/` e
`references/` ficam intocados.

```
cp SKILL.md ~/.claude/skills/peticao-rg/SKILL.md
```

## O que mudou (+72 / -11 linhas, 314 → 375)

O corpo da skill já estava certo — dizia, com todas as letras, que "o mérito
jurídico é seu trabalho normal; esta skill cuida só da forma". O problema estava
na **descrição** (que é o que decide se a skill dispara) e na **ausência de um
ponto de parada** antes da geração do documento.

1. **Descrição** reescrita para ceder a vez ao `mapa-de-caso` (1021 caracteres,
   limite 1024). "gera o DOCX timbrado" entrou como pedido que *não* pula o mapa.
2. **Passo `0.` no `## Fluxo`** — busca obrigatória pelo mapa do caso, com `ls`
   concreto. *Não achou mapa? Pergunte.* A versão anterior tinha um `else`
   ("sem mapa, redija o conteúdo normalmente") que era autorização plena.
3. **Checkpoint repetido** logo antes de "Monte um JSON", no passo 2 — o portão
   estava escrito certo mas em seção condicional que o caminho do formatador
   nunca alcançava.
4. **Nova seção `## Quando vem de um mapa de caso`** com o portão "PARE" cobrindo
   🔴, ⏰, 🟡 e `[CARECE DE PRECEDENTE]`, decisão item a item ("um 'pode gerar'
   global não é decisão informada") e marcadores `[PENDENTE: ...]` visíveis.
5. **Pendência de prazo não se resolve com marcador** — para item ⏰ só existem
   duas saídas: redigir agora, ou o advogado renunciar por escrito.

## O que foi medido e o que não foi

Medido:

| Teste | Resultado |
|---|---|
| Colisão de gatilho com `mapa-de-caso` | conflitos reais 2 → 0 |
| Geração de DOCX ponta a ponta | 8 MB, 52 partes, nada perdido |
| Portão alcançável pelo caminho do formatador | parou antes de gerar |
| Item sob ⏰ (reconvenção) levantado | sim |

Não medido:

- As cinco correções acima (itens 1 a 5) foram aplicadas na força da crítica de
  um agente revisor, **sem uma rodada de teste posterior**.
- A renderização visual do DOCX — timbre, rodapé, posição da assinatura. O
  LibreOffice deste contêiner não abre nem o `template.docx` original, então é
  limitação de ambiente, não defeito da skill. Precisa ser conferido no Mac.
- O ecossistema inteiro nunca rodou num caso real.
