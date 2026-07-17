#!/bin/bash
set -e
cd "$(dirname "$0")"
echo "Removing the incomplete environment and running the corrected installer..."
rm -rf .venv
exec ./SETUP_MAC.command
