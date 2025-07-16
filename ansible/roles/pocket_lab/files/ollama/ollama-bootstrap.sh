#!/bin/sh
# ollama-bootstrap.sh – make sure baseline models exist, else pull them.
set -eu

MODELS="llama3.2 bge-m3"               # override with $MODELS in compose
OLLAMA_HOME="${OLLAMA_HOME:-/root/.ollama}"
MANIFEST_ROOT="$OLLAMA_HOME/models/manifests/registry.ollama.ai/library"

# ---------- helper ---------------------------------------------------------
have() {             # $1 = model[:tag]
  _model="${1%%:*}"; _tag="${1#*:}"
  [ "$_model" = "$_tag" ] && _tag="latest"
  [ -f "$MANIFEST_ROOT/$_model/$_tag" ]
}



# ---------- fast-path ------------------------------------------------------
missing=""
for m in $MODELS; do have "$m" || missing="$missing $m"; done
[ -z "$missing" ] && { echo "✓ models already present"; exit 0; }

# ---------- make sure curl (and apt cache) exist --------------------------
if ! command -v curl >/dev/null 2>&1; then
  echo "Installing curl (first-run only)…"
  apt-get update -qq                                    \
    && DEBIAN_FRONTEND=noninteractive                   \
    apt-get install -y --no-install-recommends curl     \
    && rm -rf /var/lib/apt/lists/*
fi

# ---------- pull the gaps --------------------------------------------------
/bin/ollama serve &
for m in $missing; do
  echo "→ pulling $m"
  ollama pull "$m" || echo "⚠ pull failed for $m (continuing)"
done

echo "Bootstrap finished."
exit 0     # always succeed so Compose can progress
