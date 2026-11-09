#!/usr/bin/env bash
# Local toolchain: Java + Mindustry v146 server jar (load tests), Python deps for the art generators.
set -euo pipefail
cd "$(dirname "$0")/.."

if ! command -v java >/dev/null; then
  apt-get update -qq && apt-get install -y -qq openjdk-17-jre-headless >/dev/null
fi

mkdir -p .cache/mindustry
jar=.cache/mindustry/server-release.jar
[ -s "$jar" ] || curl -fsSL -o "$jar" https://github.com/Anuken/Mindustry/releases/download/v146/server-release.jar

[ -d .venv ] || uv venv -q .venv
uv pip install -q --python .venv/bin/python numpy pillow

java -version 2>&1 | head -1
ls -la "$jar"
.venv/bin/python -c "import numpy, PIL; print('numpy', numpy.__version__, 'pillow', PIL.__version__)"
