// Flags Turkish-only letters (ı, ğ, İ) that do not exist in the Turkmen
// alphabet. They usually mean a Turkish word slipped into the UI.
import { readFileSync, readdirSync, statSync } from "node:fs";
import { join, extname } from "node:path";

const roots = ["app", "components", "features", "../backend/config", "../backend/adapters"];
const exts = new Set([".ts", ".tsx", ".json", ".py"]);
const bad = /[ıİğĞ]/;
const problems = [];

function walk(dir) {
  for (const name of readdirSync(dir)) {
    const path = join(dir, name);
    if (statSync(path).isDirectory()) walk(path);
    else if (exts.has(extname(name))) {
      readFileSync(path, "utf8").split("\n").forEach((line, i) => {
        if (bad.test(line) && !line.trim().startsWith("#") && !line.trim().startsWith("//")) {
          problems.push(`${path}:${i + 1}: ${line.trim()}`);
        }
      });
    }
  }
}

roots.forEach(walk);
if (problems.length) {
  console.error(`Turkmen check failed (${problems.length}):\n${problems.join("\n")}`);
  process.exit(1);
}
console.log("Turkmen check passed: no Turkish-only letters in UI text.");
