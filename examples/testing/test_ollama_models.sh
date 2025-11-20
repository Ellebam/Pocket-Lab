#!/usr/bin/env bash
set -euo pipefail

API="${OLLAMA_HOST:-http://ollama:11434}"
JQ="$(command -v jq || true)"
if [[ -z "$JQ" ]]; then echo "jq not found. Install jq first."; exit 1; fi

MODELS=(
  "mixtral:8x7b-instruct-v0.1-q4_K_M"
  "gpt-oss:20b"
  "qwen2.5:14b"
  "qwen2.5-coder:32b-instruct"
  "qwen2.5-coder:14b"
  "phi4-mini:latest"
  "llama3.1:8b"
  "llama3.2:latest"
  "llama3.2-vision:11b"
  "bge-me:latest"
  "moondream:v2"
)

prompt="Summarize in one sentence what you are and then list 3 bullet points about reliability."
opts='{"num_predict":256,"num_ctx":4096,"num_thread":8,"temperature":0.2}'

printf "%-40s, %8s, %8s, %10s, %10s\n" "model" "tps" "ttft_ms" "eval_tokens" "total_ms"
for m in "${MODELS[@]}"; do
  # stream=false gives a single JSON with durations
  resp="$(curl -s -X POST "$API/api/generate" \
    -H "Content-Type: application/json" \
    -d "{\"model\":\"$m\",\"prompt\":\"$prompt\",\"stream\":false,\"options\":$opts}")" || resp=""

  if [[ -z "$resp" || "$(echo "$resp" | jq -r '.error? // empty')" != "" ]]; then
    printf "%-40s, %8s, %8s, %10s, %10s\n" "$m" "ERR" "ERR" "ERR" "ERR"
    continue
  fi

  eval_count=$(echo "$resp" | jq -r '.eval_count // 0')
  eval_dur_ns=$(echo "$resp" | jq -r '.eval_duration // 0')
  load_ns=$(echo "$resp" | jq -r '.load_duration // 0')
  prompt_ns=$(echo "$resp" | jq -r '.prompt_eval_duration // 0')
  total_ns=$(echo "$resp" | jq -r '.total_duration // 0')

  tps="0"
  if [[ "$eval_dur_ns" -gt 0 && "$eval_count" -gt 0 ]]; then
    tps=$(awk -v c="$eval_count" -v ns="$eval_dur_ns" 'BEGIN{printf "%.2f", c/(ns/1e9)}')
  fi
  ttft_ms=$(awk -v a="$load_ns" -v b="$prompt_ns" 'BEGIN{printf "%.0f", (a+b)/1e6}')
  total_ms=$(awk -v ns="$total_ns" 'BEGIN{printf "%.0f", ns/1e6}')

  printf "%-40s, %8s, %8s, %10s, %10s\n" "$m" "$tps" "$ttft_ms" "$eval_count" "$total_ms"
done