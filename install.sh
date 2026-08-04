#!/usr/bin/env bash

sudo apt install git

set -euo pipefail

# Detect architecture and map to ASTAP's naming convention
ARCH_RAW="$(uname -m)"

case "$ARCH_RAW" in
x86_64)
  ARCH="amd64"
  ;;
aarch64 | arm64)
  ARCH="aarch64"
  ;;
armv6l | armv7l | armhf)
  ARCH="armhf"
  ;;
*)
  echo "Unsupported architecture: $ARCH_RAW" >&2
  exit 1
  ;;
esac

echo "Detected architecture: $ARCH_RAW -> using '$ARCH'"

URL="https://sourceforge.net/projects/astap-program/files/linux_installer/astap_command-line_version_Linux_${ARCH}.zip/download"
OUTPUT="astap_cli.zip"

echo "Downloading from: $URL"
curl -L -o "$OUTPUT" "$URL"

echo "Saved as: $OUTPUT"
echo "Unzipping"
sudo apt install -y unzip
unzip astap_cli.zip
rm -rf astap_cli.zip
chmod +x astap_cli
mv astap_cli src/platesolving/astap_cli
echo "ASTAP Installed at src/platesolving/astap_cli"

echo "Installing dependencies"
sudo apt install -y build-essential libcap-dev python3-dev python3-libcamera python3-kms++

echo "Setting up python venv"
python3 -m venv --system-site-packages .venv
source .venv/bin/activate
pip install -r requirements.txt --prefer-binary
