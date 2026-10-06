#!/bin/sh
set -eu

MERGE_PUBLIC_URL="${MERGE_PUBLIC_URL:-}"
CONTAINER_WEB_ROOT="${CONTAINER_WEB_ROOT:-/app/web}"
ADDON_SOURCE="${ADDON_SOURCE:-$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)/admin-addon.js}"
TARGET="$CONTAINER_WEB_ROOT/rezeis-merge-addon.js"
INDEX="$CONTAINER_WEB_ROOT/index.html"
BACKUP="$CONTAINER_WEB_ROOT/index.html.remnawave-merge.bak"

if [ -z "$MERGE_PUBLIC_URL" ]; then
  echo "MERGE_PUBLIC_URL is required, e.g. https://merge.example.com" >&2
  exit 1
fi
if [ ! -f "$ADDON_SOURCE" ]; then
  echo "addon not found: $ADDON_SOURCE" >&2
  exit 1
fi
if [ ! -f "$INDEX" ]; then
  echo "Rezeis SPA index not found: $INDEX" >&2
  exit 1
fi

cp "$ADDON_SOURCE" "$TARGET"

if [ ! -f "$BACKUP" ]; then
  cp "$INDEX" "$BACKUP"
fi

# Remove only a previous copy of our two tags, then inject the current copy.
python3 - "$INDEX" "$MERGE_PUBLIC_URL" <<'PY'
from pathlib import Path
import html
import sys

index = Path(sys.argv[1])
base = sys.argv[2].rstrip("/")
text = index.read_text(encoding="utf-8")

start = "<!-- REMNAWAVE-SUBSCRIPTION-MERGE:START -->"
end = "<!-- REMNAWAVE-SUBSCRIPTION-MERGE:END -->"
block = (
    f"{start}"
    f"<script>window.__REMNAWAVE_MERGE_URL__={html.escape(repr(base))};</script>"
    f'<script src="/rezeis-merge-addon.js"></script>'
    f"{end}"
)

while start in text and end in text:
    a = text.index(start)
    b = text.index(end, a) + len(end)
    text = text[:a] + text[b:]

needle = "</head>"
if needle not in text:
    raise SystemExit("could not find </head> in Rezeis index.html")
text = text.replace(needle, block + needle, 1)
index.write_text(text, encoding="utf-8")
PY

echo "Installed runtime Rezeis merge addon."
echo "SPA: $INDEX"
echo "Addon: $TARGET"
echo "Merge URL: $MERGE_PUBLIC_URL"
echo "Original index backup: $BACKUP"
