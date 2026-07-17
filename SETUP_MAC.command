#!/bin/bash
set -e
cd "$(dirname "$0")"

echo "TASA Audio to Text - reliable Mac setup"
echo "This installer uses its own Python 3.11 so it will not use an incompatible system Python."
echo

if ! command -v curl >/dev/null 2>&1; then
  echo "ERROR: curl is required but was not found."
  read -p "Press Enter to close"
  exit 1
fi

if ! command -v uv >/dev/null 2>&1; then
  echo "Installing the uv Python manager..."
  curl -LsSf https://astral.sh/uv/install.sh | sh
  export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"
fi

if ! command -v uv >/dev/null 2>&1; then
  echo "ERROR: uv was installed but is not available in this Terminal session."
  echo "Close this window and run SETUP_MAC.command again."
  read -p "Press Enter to close"
  exit 1
fi

echo "Installing a compatible Python 3.11 runtime..."
uv python install 3.11

rm -rf .venv
echo "Creating the private app environment..."
uv venv --python 3.11 .venv

echo "Installing the transcription engine from prebuilt packages..."
uv pip install --python .venv/bin/python -r requirements.txt

echo
echo "Checking the installation..."
.venv/bin/python -c "import av, flask, faster_whisper; print('PyAV', av.__version__); print('faster-whisper ready')"

echo
echo "SETUP SUCCESSFUL. Now run START_MAC.command"
read -p "Press Enter to close"
