#!/bin/bash
# Manage the matrix-controller Docker container.
set -e

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_DIR"

if docker compose version &>/dev/null; then
    COMPOSE="docker compose"
elif command -v docker-compose &>/dev/null; then
    COMPOSE="docker-compose"
else
    echo "Error: docker compose is not installed." >&2
    exit 1
fi

case "${1:-}" in
    start)   sudo $COMPOSE up -d ;;
    stop)    sudo $COMPOSE down ;;
    restart) sudo $COMPOSE down && sudo $COMPOSE up -d ;;
    status)  sudo $COMPOSE ps ;;
    logs)    sudo $COMPOSE logs -f ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|logs}" >&2
        exit 1
        ;;
esac
