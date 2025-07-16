#!/bin/sh
# Ensure baseline models are present; safe to run multiple times.
set -eu

OLLAMA_MODELS="${MODELS:-llama3.2 bge-m3}"          # override via env
OLLAMA_HOME="${OLLAMA_HOME:-/root/.ollama}"
MANIFEST_ROOT="$OLLAMA_HOME/models/manifests/registry.ollama.ai/library"

have() {                                     # $1 = model[:tag]
  _model="${1%%:*}"; _tag="${1#*:}"
  [ "$_model" = "$_tag" ] && _tag="latest"
  [ -f "$MANIFEST_ROOT/$_model/$_tag" ]
}

##############################################################################
# Fast-path – nothing missing?  Quit early.
##############################################################################
missing=""
for m in $MODELS; do have "$m" || missing="$missing $m"; done
[ -z "$missing" ] && { echo "✓ models already present"; exit 0; }

##############################################################################
# First run: install curl if absent (apt cache removed afterwards)
##############################################################################
if ! command -v curl >/dev/null 2>&1; then
  echo "Installing curl (first-run only)…"
  apt-get update -qq \
    && DEBIAN_FRONTEND=noninteractive \
       apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*
fi

##############################################################################
# Start ollama in the background and wait for /api/tags to return 200
##############################################################################
/bin/ollama serve >/tmp/ollama.log 2>&1 & serve_pid=$!

echo "Waiting for Ollama REST API…"
for i in $(seq 1 30); do
  if curl -sf http://localhost:11434/api/tags >/dev/null; then
    echo "✓ server ready in ${i}s"
    break
  fi
  sleep 1
done

##############################################################################
# Pull the missing models
##############################################################################
for m in $missing; do
  echo "→ pulling $m"
  ollama pull "$m" || echo "⚠ pull failed for $m (continuing)"   # never fail hard
done

##############################################################################
# Clean up and exit
##############################################################################
kill "$serve_pid"            # shut down background server gracefully
echo "Bootstrap finished."
exit 0                       # Compose sees success
