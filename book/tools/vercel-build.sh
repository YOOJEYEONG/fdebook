#!/usr/bin/env bash
# Vercel Git build (Amazon Linux 2023 build image) and local equivalent: pinned Exact, Bun and
# Exact's web tools (official `setup --platform web`), then book/ → .vercel/output (dist/ only).
set -euo pipefail
EXACT_COMMIT=de212e671a69f4fea18bed67d5b73b259ddf3061
BUN_VERSION=1.4.2

root=$(cd "$(dirname "$0")/../.." && pwd)
exact="$root/.cache-ext/exact"
export EXACT_FEEDBACK=0 BUN_INSTALL="$HOME/.bun-$BUN_VERSION"
export PATH="$BUN_INSTALL/bin:$HOME/.cargo/bin:$PATH"

# Linker for Rust build scripts, unzip for the Bun installer (dnf: the build image's package manager).
for pair in cc:gcc unzip:unzip git:git; do
  command -v "${pair%%:*}" >/dev/null || dnf install -y "${pair#*:}"
done
[ -x "$BUN_INSTALL/bin/bun" ] || curl -fsSL https://bun.sh/install | bash -s "bun-v$BUN_VERSION"
command -v rustup >/dev/null || curl -fsSL https://sh.rustup.rs | sh -s -- -y --profile minimal --default-toolchain none --no-modify-path

if [ ! -d "$exact" ]; then
  git init -q "$exact"
  git -C "$exact" fetch -q --depth 1 https://github.com/expo/exact.git "$EXACT_COMMIT"
  git -C "$exact" checkout -q FETCH_HEAD
fi
have=$(git -C "$exact" rev-parse HEAD)
[ "$have" = "$EXACT_COMMIT" ] || { echo "$exact is at $have, not $EXACT_COMMIT" >&2; exit 1; }

# Pinned stable + web nightly Rust, wasm-bindgen, Binaryen, node_modules, Chromium, locked crates.
(cd "$exact" && bun scripts/exact.mjs setup --platform web)

cd "$root/book"
bun run build
bun tools/vercel-output.ts
