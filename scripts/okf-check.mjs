import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const okfRoot = path.join(root, "okf");
const errors = [];

function walk(dir) {
  return fs.readdirSync(dir, { withFileTypes: true }).flatMap((entry) => {
    const full = path.join(dir, entry.name);
    return entry.isDirectory() ? walk(full) : [full];
  });
}

function relative(file) {
  return path.relative(root, file).split(path.sep).join("/");
}

function frontmatter(text) {
  if (!text.startsWith("---\n")) return null;
  const end = text.indexOf("\n---\n", 4);
  if (end === -1) return null;
  return text.slice(4, end);
}

for (const required of ["index.md", "service.md", "capabilities/index.md", "qa/index.md", "log.md"]) {
  if (!fs.existsSync(path.join(okfRoot, required))) {
    errors.push(`missing required file: okf/${required}`);
  }
}

const markdownFiles = fs.existsSync(okfRoot)
  ? walk(okfRoot).filter((file) => file.endsWith(".md"))
  : [];

for (const file of markdownFiles) {
  const name = relative(file);
  const text = fs.readFileSync(file, "utf8");
  const meta = frontmatter(text);

  if (!meta) {
    errors.push(`${name}: missing YAML frontmatter`);
    continue;
  }
  if (!/^type:\s*\S+/m.test(meta)) {
    errors.push(`${name}: frontmatter needs a non-empty type`);
  }
  if (name !== "okf/index.md" && /^okf_version:/m.test(meta)) {
    errors.push(`${name}: okf_version belongs only in okf/index.md`);
  }
  const status = meta.match(/^status:\s*(.+)$/m)?.[1]?.trim();
  if (status && status !== "stub" && !name.includes("/_proposals/")) {
    errors.push(`${name}: status belongs only in the workspace roadmap`);
  }

  for (const match of text.matchAll(/\[[^\]]+\]\(([^)]+)\)/g)) {
    const target = match[1].split("#")[0].trim();
    if (!target || /^(?:https?:|mailto:|[a-z0-9-]+:)/i.test(target)) continue;
    const resolved = target.startsWith("/")
      ? path.join(okfRoot, target.slice(1))
      : path.resolve(path.dirname(file), target);
    if (!fs.existsSync(resolved)) errors.push(`${name}: broken link ${target}`);
  }

  if (name.startsWith("okf/capabilities/") && !name.endsWith("/index.md")) {
    if (!/^#### Scenario:/m.test(text)) errors.push(`${name}: capability has no scenario`);
    if (!/^\*\*Checked by:\*\*/m.test(text)) errors.push(`${name}: scenario has no Checked by line`);
    const qa = path.join(okfRoot, "qa", path.basename(file));
    if (!fs.existsSync(qa)) errors.push(`${name}: missing matching QA checklist`);
  }

  if (name.startsWith("okf/qa/") && !name.endsWith("/index.md")) {
    if (!/^### Check:/m.test(text)) errors.push(`${name}: checklist has no checks`);
    for (const field of ["Requirement", "Surface", "Automated"]) {
      if (!new RegExp(`^\\*\\*${field}:\\*\\*\\s*\\S+`, "m").test(text)) {
        errors.push(`${name}: check is missing ${field}`);
      }
    }
    if (!/^\*\*Do:\*\*/m.test(text)) errors.push(`${name}: check is missing Do`);
    if (!/^\*\*Expect:\*\*/m.test(text)) errors.push(`${name}: check is missing Expect`);
  }
}

if (errors.length) {
  console.error(`OKF conformance failed (${errors.length}):`);
  for (const error of errors) console.error(`- ${error}`);
  process.exit(1);
}

console.log(`OKF conformance passed (${markdownFiles.length} markdown files).`);
