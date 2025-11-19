# scripts/check_environment_md.sh
set -euo pipefail
f="docs/ENVIRONMENT.md"

# 1) No leading indentation on table lines
if grep -nE '^[[:space:]]+\|' "$f"; then
  echo "ERROR: Indented table detected in $f"
  exit 1
fi

# 2) Header separator line must match header column count
#    (simple heuristic: the line right after a header row must be pipes+hyphens)
awk '
  prev_header=0
  /^\|/ {
    if (prev_header==1) {
      if ($0 !~ /^\|[[:space:]-]+\|$/) {
        print "ERROR: Missing/misaligned separator after header at line " NR-1
        exit 2
      }
      prev_header=0
    }
  }
  /^\|/ && $0 ~ /\|/ && $0 ~ /---/ && prev_header==0 { } # data row
  /^\|/ && $0 !~ /---/ { prev_header=1 } # header row candidate
' "$f"
