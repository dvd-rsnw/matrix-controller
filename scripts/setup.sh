#!/bin/bash
# One-time setup on a Raspberry Pi: Docker, .env, container, systemd unit.
set -e

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_DIR"

echo "== matrix-controller setup =="

# 1. Docker
if ! command -v docker &>/dev/null; then
    echo "Installing Docker..."
    curl -sSL https://get.docker.com | sh
fi
sudo systemctl start docker

# 2. .env
if [ ! -f .env ]; then
    echo "Train API URL (see docs/api-contract.md.) Leave empty for demo mode:"
    read -r API_URL
    if [ -n "$API_URL" ]; then
        echo "TRAIN_API_URL=$API_URL" > .env
    else
        touch .env
    fi
    echo "Wrote .env"
fi

# 3. Build and start
sudo docker compose up -d --build

# 4. systemd unit for boot autostart
echo "Enable start-on-boot via systemd? (Y/n)"
read -r ENABLE
if [[ -z "$ENABLE" || "$ENABLE" =~ ^[Yy]$ ]]; then
    sudo tee /etc/systemd/system/matrix-display.service > /dev/null << EOF
[Unit]
Description=LED Matrix Train Display
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=$REPO_DIR
ExecStart=$REPO_DIR/scripts/run.sh start
ExecStop=$REPO_DIR/scripts/run.sh stop

[Install]
WantedBy=multi-user.target
EOF
    sudo systemctl daemon-reload
    sudo systemctl enable matrix-display.service
    echo "Enabled matrix-display.service"
fi

echo "Done. Useful commands: scripts/run.sh {start|stop|restart|status|logs}"
