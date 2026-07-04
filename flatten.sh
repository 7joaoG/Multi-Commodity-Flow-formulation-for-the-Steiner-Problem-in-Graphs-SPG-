#!/bin/bash

# flatten.sh - Gera flattened-codebase.xml com a estrutura e conteúdo do código-fonte
# Uso: execute no diretório raiz do projeto

OUTPUT_FILE="flattened-codebase.xml"

# Diretórios a serem ignorados (subdiretórios comuns de bibliotecas/build/cache)
IGNORE_DIRS=(
    "node_modules"
    ".git"
    "dist"
    "build"
    ".next"
    ".nuxt"
    "__pycache__"
    ".cache"
    "coverage"
    ".vscode"
    ".idea"
    "logs"
    "tmp"
    "temp"
)

# Padrões de arquivos a serem ignorados (extensões/binários)
IGNORE_PATTERNS=(
    "*.stp"
    "*.lock"
    "*.log"
    "*.bak"
    "*.png"
    "*.jpg"
    "*.jpeg"
    "*.gif"
    "*.ico"
    "*.pdf"
    "*.zip"
    "*.tar"
    "*.gz"
    "*.exe"
    "*.dll"
    "*.so"
    "*.dylib"
    "*.bin"
    "*.pyc"
    "*.class"
    "*.o"
    "*.obj"
)

# Nome do próprio arquivo de saída (para não incluir ele mesmo)
OUTPUT_BASENAME=$(basename "$OUTPUT_FILE")

# Função para escapar conteúdo como CDATA (lida com "]]>" interno)
write_cdata() {
    local content="$1"
    # Divide o conteúdo em partes por "]]>" e coloca entre seções CDATA
    if [[ "$content" == *"]]>"* ]]; then
        local first="${content%%]]>*}"
        local rest="${content#*]]>}"
        printf "<![CDATA[%s]]]]><![CDATA[>%s]]>" "$first" "$rest"
    else
        printf "<![CDATA[%s]]>" "$content"
    fi
}

# Inicia o arquivo XML
echo '<?xml version="1.0" encoding="UTF-8"?>' > "$OUTPUT_FILE"
echo '<codebase>' >> "$OUTPUT_FILE"

# Monta argumentos para o find: exclusão de diretórios
find_args=()
for dir in "${IGNORE_DIRS[@]}"; do
    find_args+=(-not -path "*/$dir/*" -not -path "*/$dir")
done

# Adiciona exclusão do próprio arquivo de saída
find_args+=(-not -name "$OUTPUT_BASENAME")

# Adiciona exclusão por padrões de arquivo (usando -not -name)
for pattern in "${IGNORE_PATTERNS[@]}"; do
    find_args+=(-not -name "$pattern")
done

# Encontra todos os arquivos (type f) e processa
find . -type f "${find_args[@]}" | while IFS= read -r file; do
    # Remove o "./" do início do caminho
    rel_path="${file#./}"

    # Verifica se é um arquivo de texto (usando file e grep -I)
    if file -b --mime-type "$file" | grep -q "^text/"; then
        is_text=1
    elif grep -qI '.' "$file" 2>/dev/null; then
        is_text=1
    else
        is_text=0
    fi

    if [ "$is_text" -eq 1 ]; then
        # Lê o conteúdo do arquivo
        content=$(cat "$file" 2>/dev/null)
        if [ $? -ne 0 ]; then
            content="[ERRO: não foi possível ler o arquivo]"
        fi
    else
        content="[ARQUIVO BINÁRIO OU NÃO TEXTO - CONTEÚDO OMITIDO]"
    fi

    # Escreve o bloco XML
    echo "  <file path=\"$rel_path\">" >> "$OUTPUT_FILE"
    echo "    <content>" >> "$OUTPUT_FILE"
    printf "      " >> "$OUTPUT_FILE"
    write_cdata "$content" >> "$OUTPUT_FILE"
    printf "\n" >> "$OUTPUT_FILE"
    echo "    </content>" >> "$OUTPUT_FILE"
    echo "  </file>" >> "$OUTPUT_FILE"
done

# Finaliza o XML
echo '</codebase>' >> "$OUTPUT_FILE"

echo "✅ Arquivo gerado: $OUTPUT_FILE"