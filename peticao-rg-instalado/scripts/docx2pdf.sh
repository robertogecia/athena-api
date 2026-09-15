#!/bin/bash
# Converte DOCX em PDF com fidelidade total ao modelo (fontes embutidas).
# Preferência: LibreOffice (silencioso). Fallback: Microsoft Word.
#
# HISTÓRICO: até jul/2026 este script copiava o DOCX para dentro do
# container sandbox do Word (~/Library/Containers/com.microsoft.Word/Data)
# antes de abrir, para evitar um diálogo modal de "Conceder Acesso" que
# travava o AppleScript (-609/-1712) ao abrir arquivo de fora do sandbox.
# Isso quebrou depois de uma atualização do macOS: o `cp` para dentro do
# container passou a ser barrado com "Operation not permitted" (proteção
# do sistema, não da skill). Testado: abrir o arquivo DIRETO do caminho
# original com `open -a` funciona sem o diálogo modal (o Launch Services
# do macOS concede acesso ao arquivo automaticamente nesse fluxo, diferente
# de uma cópia bruta via `cp`) — não precisa mais do passo de sandbox.
#
# ATUALIZAÇÃO (14/07/2026): o comando `save as d file name "$PDF" ...`
# passou a falhar sempre com "active document não entende a mensagem
# save as" (-1708) nesta build do Word (16.110.3), mesmo com o documento
# certo aberto e outras properties/commands (name, path, save simples)
# respondendo normalmente. A causa era o parâmetro `file name` receber uma
# string bruta — coagir para `(POSIX file "$PDF")` resolveu; sem isso,
# o dictionary do Word rejeita a mensagem inteira antes mesmo de validar
# o formato PDF.
#
# Uso: ./docx2pdf.sh "/caminho/Peticao.docx" [saida.pdf]

set -e
DOCX="$1"
[ -z "$DOCX" ] && { echo "Uso: docx2pdf.sh arquivo.docx [saida.pdf]"; exit 1; }
DOCX="$(cd "$(dirname "$DOCX")" && pwd)/$(basename "$DOCX")"
PDF="${2:-${DOCX%.docx}.pdf}"

SOFFICE=""
for c in soffice /Applications/LibreOffice.app/Contents/MacOS/soffice; do
  command -v "$c" >/dev/null 2>&1 && SOFFICE="$c" && break
done

if [ -n "$SOFFICE" ]; then
  OUTDIR="$(dirname "$PDF")"
  "$SOFFICE" --headless --convert-to pdf --outdir "$OUTDIR" "$DOCX" >/dev/null
  GEN="$OUTDIR/$(basename "${DOCX%.docx}").pdf"
  [ "$GEN" != "$PDF" ] && mv "$GEN" "$PDF"
elif [ -d "/Applications/Microsoft Word.app" ]; then
  BASE="$(basename "${DOCX%.docx}").docx"
  # NUNCA use `pkill -9` no Word aqui: se o usuário tiver outro documento
  # aberto com alterações não salvas (ex.: algo em que já estava
  # trabalhando, sem relação com esta skill), um kill força o encerramento
  # sem salvar. Descoberto em 14/07/2026: matou o Word com dois outros
  # DOCX abertos; um deles ("Fulano - Alvara.docx", fora desta skill)
  # voltou com `saved=false` na recuperação automática do Word — risco real
  # de perda de trabalho do usuário. `open -a` sozinho basta: se o Word já
  # estiver rodando, ele só abre este arquivo como nova janela na mesma
  # sessão, sem derrubar nada.
  open -a "Microsoft Word" "$DOCX"

  # sonda até o documento aparecer na lista de abertos (máx ~180s; DOCX de
  # ~8MB com fontes embutidas em pasta OneDrive já levou mais de 90s em
  # teste real de 14/07/2026). Checa por NOME entre todos os documentos
  # abertos, não por "active document" — com outras janelas do Word já
  # abertas, o foco pode não ir para o arquivo recém-aberto.
  FOUND=""
  for i in $(seq 1 90); do
    FOUND=$(osascript -e "with timeout of 5 seconds
      tell application \"Microsoft Word\" to return (exists document \"$BASE\")
    end timeout" 2>/dev/null || true)
    [ "$FOUND" = "true" ] && break
    sleep 2
  done
  [ "$FOUND" != "true" ] && { echo "ERRO: Word não abriu o documento (diálogo modal? primeira execução?)" >&2; exit 3; }

  # referencia o documento pelo NOME explícito (não "active document"):
  # com múltiplos documentos abertos, "active document" pode apontar para
  # a janela errada. O "close" às vezes falha de forma inofensiva logo
  # após o "save as" para PDF (a referência ao objeto muda de estado); por
  # isso roda em bloco `try` próprio e não derruba o script — a checagem
  # real de sucesso é a existência do PDF no final.
  osascript <<EOF
with timeout of 180 seconds
  tell application "Microsoft Word"
    save as document "$BASE" file name (POSIX file "$PDF") file format format PDF
    try
      close document "$BASE" saving no
    end try
  end tell
end timeout
EOF
else
  echo "ERRO: nem LibreOffice nem Microsoft Word encontrados." >&2
  echo "Abra o DOCX no Word e exporte como PDF manualmente." >&2
  exit 2
fi

[ -f "$PDF" ] && echo "OK: $PDF" || { echo "ERRO: PDF não foi gerado" >&2; exit 3; }
