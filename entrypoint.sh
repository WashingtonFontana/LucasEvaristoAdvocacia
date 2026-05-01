#!/bin/sh
# entrypoint.sh — Startup script for Railway deployment
#
# 1. If DATA_DIR is set (Railway volume), copy initial images to volume
# 2. Initialize databases and admin user (idempotent)
# 3. Start uvicorn

if [ -n "$DATA_DIR" ]; then
    mkdir -p "${DATA_DIR}/img"
    if [ -z "$(ls -A "${DATA_DIR}/img" 2>/dev/null)" ]; then
        cp -r /app/static/img/* "${DATA_DIR}/img/" 2>/dev/null || true
    fi
fi

python init_db.py

exec uvicorn app:app --host 0.0.0.0 --port "${PORT:-8000}"