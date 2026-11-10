#!/usr/bin/env bash
# Lighthouse scores for SHIVAS pages, served from site/ with gzip (like the real host).
#   tools/lighthouse.sh                         # home, galvanizing, items/kettle; phone + desktop
#   tools/lighthouse.sh items/slm.html blog/index.html
# Installs Lighthouse once into ~/.cache/shivas-lighthouse. JSON reports go to preview/lighthouse/.
set -euo pipefail
cd "$(dirname "$0")/.."
LH="$HOME/.cache/shivas-lighthouse"
if [ ! -x "$LH/node_modules/.bin/lighthouse" ]; then
  mkdir -p "$LH" && (cd "$LH" && npm init -y >/dev/null && npm i -s lighthouse@12 >/dev/null)
fi
CHROME="${CHROME_PATH:-/opt/pw-browsers/chromium}"
[ -x "$CHROME" ] || CHROME="$(node -e "console.log(require('playwright').chromium.executablePath())")"
PORT=8799
node tools/screenshot.cjs --serve --port $PORT >/dev/null 2>&1 & SRV=$!
trap 'kill $SRV 2>/dev/null' EXIT
sleep 1
mkdir -p preview/lighthouse
PAGES=("$@"); [ ${#PAGES[@]} -eq 0 ] && PAGES=(index.html galvanizing.html items/kettle.html)
printf "%-28s %-8s %5s %5s %5s %5s  %s\n" page form perf a11y best seo "LCP / CLS / TBT"
for p in "${PAGES[@]}"; do
  for form in mobile desktop; do
    out="preview/lighthouse/$(echo "$p" | tr / _)-$form.json"
    extra=(); [ $form = desktop ] && extra=(--preset=desktop)
    CHROME_PATH="$CHROME" node "$LH/node_modules/lighthouse/cli/index.js" "http://127.0.0.1:$PORT/$p" "${extra[@]}" \
      --quiet --chrome-flags="--headless=new --no-sandbox" --only-categories=performance,accessibility,best-practices,seo \
      --output=json --output-path="$out" >/dev/null 2>&1 || { echo "$p $form: lighthouse failed"; continue; }
    python3 - "$out" "$p" "$form" <<'PY'
import json,sys
r=json.load(open(sys.argv[1])); c=r['categories']; a=r['audits']
s=lambda k: round((c[k]['score'] or 0)*100)
print(f"{sys.argv[2]:<28} {sys.argv[3]:<8} {s('performance'):>5} {s('accessibility'):>5} {s('best-practices'):>5} {s('seo'):>5}  "
      f"{a['largest-contentful-paint']['displayValue']} / {a['cumulative-layout-shift']['displayValue']} / {a['total-blocking-time']['displayValue']}")
for k,v in a.items():
    if v.get('score') is not None and v['score']<0.9 and v.get('scoreDisplayMode')=='binary' and k not in ('errors-in-console',):
        print(f"{'':<38}fail: {k}")
PY
  done
done
