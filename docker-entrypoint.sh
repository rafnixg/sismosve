#!/bin/sh
set -eu
mkdir -p /app/logs
exec python run.py prod
