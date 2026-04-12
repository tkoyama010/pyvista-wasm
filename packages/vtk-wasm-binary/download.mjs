#!/usr/bin/env node

/**
 * Download the VTK.wasm binary from upstream Kitware GitLab.
 *
 * Usage:
 *   node download.mjs [version]
 *
 * If no version is given, it reads the version from package.json.
 */

import { createWriteStream } from "node:fs";
import { readFile } from "node:fs/promises";
import { pipeline } from "node:stream/promises";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const __dirname = dirname(fileURLToPath(import.meta.url));

const pkg = JSON.parse(
  await readFile(join(__dirname, "package.json"), "utf8"),
);
const version = process.argv[2] || pkg.version;

const url =
  `https://gitlab.kitware.com/api/v4/projects/13/packages/generic/` +
  `vtk-wasm32-emscripten/${version}/vtk-${version}-wasm32-emscripten.tar.gz`;

const outPath = join(__dirname, "vtk-wasm32-emscripten.tar.gz");

console.log(`Downloading VTK.wasm ${version}...`);
console.log(`  Source: ${url}`);

const res = await fetch(url, { redirect: "follow" });
if (!res.ok) {
  console.error(`Download failed: ${res.status} ${res.statusText}`);
  process.exit(1);
}

await pipeline(res.body, createWriteStream(outPath));

console.log(`  Saved to: ${outPath}`);
