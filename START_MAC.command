#!/bin/bash
set -e
cd "$(dirname "$0")"
if [ ! -x .venv/bin/python ]; then
  echo "The app is not installed yet. Run SETUP_MAC.command first."
  read -p "Press Enter to close"
  exit 1
fi
open http://localhost:8787
.venv/bin/python server.py
