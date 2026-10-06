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
node - "$INDEX" "$MERGE_PUBLIC_URL" <<'NODE'
const fs = require("node:fs");
const index = process.argv[2];
const base = process.argv[3].replace(/\\/+$/, "");
let text = fs.readFileSync(index, "utf8");

const start = "<!-- REMNAWAVE-SUBSCRIPTION-MERGE:START -->";
const end = "<!-- REMNAWAVE-SUBSCRIPTION-MERGE:END -->";
const block =
  start +
  "<script>window.__REMNAWAVE_MERGE_URL__=" + JSON.stringify(base) + ";</script>" +
  '<script src="/rezeis-merge-addon.js"></script>' +
  end;

while (text.includes(start) && text.includes(end)) {
  const a = text.indexOf(start);
  const b = text.indexOf(end, a) + end.length;
  text = text.slice(0, a) + text.slice(b);
}

if (!text.includes("</head>")) {
  throw new Error("could not find </head> in Rezeis index.html");
}
text = text.replace("</head>", block + "</head>", 1);
fs.writeFileSync(index, text, "utf8");
NODE

echo "Installed runtime Rezeis merge addon."
echo "SPA: $INDEX"
echo "Addon: $TARGET"
echo "Merge URL: $MERGE_PUBLIC_URL"
echo "Original index backup: $BACKUP"
