#!/usr/bin/env bash
# Runs the real Mindustry v146 desktop client (Xvfb + Mesa llvmpipe) with the mod and the test stand.
# Output: build/shots/*.png, build/shots/manifest.json, build/client.log
set -euo pipefail
cd "$(dirname "$0")/.."
jar="$PWD/.cache/mindustry/Mindustry.jar"
[ -s "$jar" ] || curl -fsSL -o "$jar" https://github.com/Anuken/Mindustry/releases/download/v146/Mindustry.jar

version=$(sed -n 's/^version: *"\(.*\)"/\1/p' mod/mod.hjson)
mkdir -p build
zip="build/vanguard-arsenal-$version.zip"
rm -f "$zip" build/vgtest.zip
(cd mod && zip -q -r -X "../$zip" .)
(cd tools/harness && zip -q -r -X ../../build/vgtest.zip .)

data=$PWD/build/client-data
rm -rf "$data" build/shots && mkdir -p "$data/Mindustry/mods" build/shots
cp "$zip" "$data/Mindustry/mods/"
cp build/vgtest.zip "$data/Mindustry/mods/"

pgrep -x Xvfb >/dev/null || { Xvfb :99 -screen 0 1280x800x24 >/dev/null 2>&1 & sleep 2; }
DISPLAY=:99 XDG_DATA_HOME="$data" timeout "${CLIENT_TIMEOUT:-300}" java -jar "$jar" 2>&1 \
  | grep -v '^ALSA lib\|^Jack\|jack server\|Cannot connect to server' | sed 's/\x1b\[[0-9;]*m//g' > build/client.log || true

cp -r "$data/Mindustry/vgtest/." build/shots/ 2>/dev/null || true
echo "--- log (errors / vg lines):"
grep -nE '\[E\]|\[W\]|\[vg|Exception' build/client.log | grep -v 'community servers\|Failed to initialize audio' | head -60 || true
echo "--- shots: $(ls build/shots/*.png 2>/dev/null | wc -l)"
