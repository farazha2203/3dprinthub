#!/usr/bin/env bash
set -euo pipefail
PROJECT_ROOT="${1:-/var/www/3dprinthub}"
SERVICE_NAME="3dprinthub-link-worker.service"
sudo cp "$PROJECT_ROOT/deploy/systemd/$SERVICE_NAME" "/etc/systemd/system/$SERVICE_NAME"
sudo systemctl daemon-reload
sudo systemctl enable --now "$SERVICE_NAME"
sudo systemctl status "$SERVICE_NAME" --no-pager
