#!/bin/bash
set -e

echo ""
echo "=== Buzzinga Setup ==="
echo ""

# Check for uv
if ! command -v uv &> /dev/null; then
    echo "uv is not installed. You need it for this setup."
    echo "Install it from: https://docs.astral.sh/uv/getting-started/installation/"
    echo ""
    echo "The quickest way:"
    echo "  curl -LsSf https://astral.sh/uv/install.sh | sh"
    echo ""
    exit 1
fi

# Ask where to install
DEFAULT_DIR="$HOME/Desktop/Buzzinga"
echo "Where do you want to install Buzzinga?"
read -p "Press Enter for default ($DEFAULT_DIR) or type a path: " INSTALL_DIR
INSTALL_DIR="${INSTALL_DIR:-$DEFAULT_DIR}"

# Expand ~ if the user typed it
INSTALL_DIR="${INSTALL_DIR/#\~/$HOME}"

if [ -d "$INSTALL_DIR" ]; then
    echo ""
    echo "The folder $INSTALL_DIR already exists."
    read -p "Overwrite? (y/N): " OVERWRITE
    if [[ ! "$OVERWRITE" =~ ^[Yy]$ ]]; then
        echo "Setup cancelled."
        exit 0
    fi
fi

echo ""
echo "Building Buzzinga... (this may take a minute the first time)"
echo ""

# Build the executable
uv run pyinstaller launcher.py --onefile \
    --add-data "src/buzzinga/staticfiles:staticfiles" \
    --name buzzinga \
    --paths src \
    --log-level WARN

echo ""
echo "Setting up your game folder..."

# Create install directory and data subfolders
mkdir -p "$INSTALL_DIR/data/images"
mkdir -p "$INSTALL_DIR/data/sounds"
mkdir -p "$INSTALL_DIR/data/hints"
mkdir -p "$INSTALL_DIR/data/questions"
mkdir -p "$INSTALL_DIR/data/who-knows-more"

# Copy executable
cp dist/buzzinga "$INSTALL_DIR/buzzinga"
chmod +x "$INSTALL_DIR/buzzinga"

echo ""
echo "=== Done! ==="
echo ""
echo "Buzzinga is installed at: $INSTALL_DIR"
echo ""
echo "To play, double-click the 'buzzinga' file in that folder."
echo ""
echo "Don't forget to add your quiz content to the data/ folder!"
echo "See the README for details on game data formats."
echo ""
