#!/bin/bash

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENTRY="$SCRIPT_DIR/xyron_codex.py"

echo ""
echo "  ██╗  ██╗██╗   ██╗██████╗  ██████╗ ███╗  ██╗"
echo "  ╚██╗██╔╝╚██╗ ██╔╝██╔══██╗██╔═══██╗████╗ ██║"
echo "   ╚███╔╝  ╚████╔╝ ██████╔╝██║   ██║██╔██╗██║"
echo "   ██╔██╗   ╚██╔╝  ██╔══██╗██║   ██║██║╚████║"
echo "  ██╔╝╚██╗   ██║   ██║  ██║╚██████╔╝██║ ╚███║"
echo "  ╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚══╝"
echo ""
echo "  Install Script  ·  by ShadowNex"
echo ""


PYTHON=""
if command -v python3 &>/dev/null; then
    PYTHON=$(command -v python3)
elif command -v python &>/dev/null; then
    PYTHON=$(command -v python)
else
    echo "  ERROR: Python tidak ditemukan."
    exit 1
fi
echo "  ✓  Python: $PYTHON"


echo "  ⟳  Menginstall dependencies..."
if [ -n "$PREFIX" ]; then
    # Termux
    "$PYTHON" -m pip install httpx python-dotenv rich --break-system-packages -q 2>/dev/null \
        || "$PYTHON" -m pip install httpx python-dotenv rich -q
else
    "$PYTHON" -m pip install httpx python-dotenv rich -q 2>/dev/null \
        || "$PYTHON" -m pip install httpx python-dotenv rich --break-system-packages -q
fi
echo "  ✓  Dependencies OK"


if [ -n "$PREFIX" ]; then

    BIN_DIR="$PREFIX/bin"
elif [ -d "$HOME/.local/bin" ]; then
    BIN_DIR="$HOME/.local/bin"
else
    mkdir -p "$HOME/.local/bin"
    BIN_DIR="$HOME/.local/bin"
fi


WRAPPER_PATH="$BIN_DIR/xyroncodex"

cat > "$WRAPPER_PATH" << WRAPPER
#!/bin/bash
exec "$PYTHON" "$ENTRY" "\$@"
WRAPPER

chmod +x "$WRAPPER_PATH"
echo "  ✓  Command dibuat : $WRAPPER_PATH"



if ! echo "$PATH" | grep -q "$BIN_DIR"; then

    SHELL_RC=""
    if [ -n "$BASH_VERSION" ] && [ -f "$HOME/.bashrc" ]; then
        SHELL_RC="$HOME/.bashrc"
    elif [ -n "$ZSH_VERSION" ] && [ -f "$HOME/.zshrc" ]; then
        SHELL_RC="$HOME/.zshrc"
    elif [ -f "$HOME/.bashrc" ]; then
        SHELL_RC="$HOME/.bashrc"
    elif [ -f "$HOME/.profile" ]; then
        SHELL_RC="$HOME/.profile"
    fi

    if [ -n "$SHELL_RC" ]; then
        if ! grep -q "export PATH.*$BIN_DIR" "$SHELL_RC" 2>/dev/null; then
            echo "" >> "$SHELL_RC"
            echo "# Xyron Codex" >> "$SHELL_RC"
            echo "export PATH=\"$BIN_DIR:\$PATH\"" >> "$SHELL_RC"
            echo "  ✓  PATH ditambah ke $SHELL_RC"
        fi
    fi

    echo ""
    echo "  ─────────────────────────────────────"
    echo "  Jalankan ini agar langsung aktif:"
    echo ""
    echo "    export PATH=\"$BIN_DIR:\$PATH\""
    echo ""
    echo "  Atau tutup & buka terminal baru."
    echo "  ─────────────────────────────────────"
else
    echo "  ✓  PATH sudah benar"
fi

echo ""
echo "  ✓  SELESAI! Sekarang ketik:"
echo ""
echo "       xyroncodex"
echo ""
