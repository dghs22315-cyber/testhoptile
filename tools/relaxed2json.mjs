#!/usr/bin/env node
// Converts a "relaxed" Hjson file (bare keys/values, inline `{ a: b, c: d }` objects) to strict JSON.
// Unlike Hjson, a bare value ends at , } ] or newline, so one-line objects keep their closing braces.
import fs from "node:fs";

const [src, dst] = process.argv.slice(2);
const text = fs.readFileSync(src, "utf8").replace(/^\s*\/\/.*$/gm, "").replace(/^\s*#.*$/gm, "");
let i = 0;

const ws = () => { while (i < text.length && /[\s,]/.test(text[i])) i++; };
const fail = (m) => { throw new Error(`${m} at offset ${i}: ${JSON.stringify(text.slice(i, i + 40))}`); };

function bare() {
  const m = /^[^\s{}\[\],:"]+(?:[ \t]+[^\s{}\[\],:"]+)*/.exec(text.slice(i));
  if (!m) fail("expected value");
  i += m[0].length;
  const s = m[0];
  if (s === "true") return true;
  if (s === "false") return false;
  if (s === "null") return null;
  if (/^-?(\d+\.?\d*|\.\d+)([eE][-+]?\d+)?$/.test(s)) return Number(s);
  return s;
}

function str() {
  const m = /^"(?:[^"\\]|\\.)*"/.exec(text.slice(i));
  if (!m) fail("bad string");
  i += m[0].length;
  return JSON.parse(m[0]);
}

function key() {
  ws();
  const k = text[i] === '"' ? str() : bare();
  ws();
  if (text[i] !== ":") fail("expected ':'");
  i++;
  return String(k);
}

function value() {
  ws();
  const c = text[i];
  if (c === "{") {
    i++;
    const o = {};
    for (;;) { ws(); if (text[i] === "}") { i++; return o; } const k = key(); o[k] = value(); }
  }
  if (c === "[") {
    i++;
    const a = [];
    for (;;) { ws(); if (text[i] === "]") { i++; return a; } a.push(value()); }
  }
  if (c === '"') return str();
  return bare();
}

// Top level may omit the outer braces (Hjson root object).
ws();
let root;
if (text[i] === "{") root = value();
else {
  root = {};
  for (;;) { ws(); if (i >= text.length) break; const k = key(); root[k] = value(); }
}
fs.writeFileSync(dst, JSON.stringify(root, null, 2) + "\n");
console.log(`${src} -> ${dst}: ${Object.keys(root).length} top-level keys`);
