#!/usr/bin/env bash

sudo apt update
sudo apt upgrade
sudo apt install git vim 

mkdir -p /home/pi/images
mkdir -p /home/pi/images/QuadStar

# Startup script setup
echo "#!/bin/bash

# /etc/init.d/quadstar-startup.sh
### BEGIN INIT INFO
# Provides:          quadstar-startup
# Required-Start:    $remote_fs $syslog
# Required-Stop:     $remote_fs $syslog
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: Start daemon at boot time
# Description:       Enable service provided by daemon.
### END INIT INFO

sudo bash /home/pi/startup.sh > /home/pi/startup_logs/startup_$(date +%s).log 2>&1" > /etc/init.d/quadstar-startup.sh
chmod +x /etc/init.d/quadstar-startup.sh
update-rc.d quadstar-startup.sh default

echo "#!/bin/bash
cd /home/pi/QuadStar_Auxillary_Computer
source .venv/bin/activate
python3 src/main.py 0.3 1.0 3
chown -R pi:pi /home/pi/images/
./sync.sh
"> /home/pi/startup.sh
chmod +x /home/pi/startup.sh
mkdir -p /home/pi/startup_logs

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
sudo apt install -y build-essential libcap-dev python3-dev python3-libcamera python3-kms++ apt-listchanges

echo "Setting up python venv"
python3 -m venv --system-site-packages .venv
source .venv/bin/activate
pip install -r requirements.txt --prefer-binary

