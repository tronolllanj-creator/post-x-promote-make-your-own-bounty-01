import { readFileSync, writeFileSync, mkdirSync } from "node:fs";

// Decide where the bot work and outputs live from the environment.
const workArea = process.env["MAKEFUN_BOT_DIR"] || "/bot";
const dropArea = process.env["MAKEFUN_OUTPUT_DIR"] || "/output";

function fail(msg: string): never {
  process.stderr.write(msg + "\n");
  process.exit(1);
}

let rawBytes: Buffer;
try {
  rawBytes = readFileSync(`${workArea}/POST.json`);
} catch (err) {
  fail(`could not read POST.json from ${workArea}: ${String(err)}`);
}

let record: unknown;
try {
  record = JSON.parse(rawBytes.toString("utf8"));
} catch (err) {
  fail(`the payload does not parse as JSON: ${String(err)}`);
}

// Confirm the payload is a plain object (not null and not an array).
if (typeof record !== "object" || record === null || Array.isArray(record)) {
  fail("the payload must be a JSON object");
}

// The url field has to exist, be a string, and point at an https link.
const candidate = (record as { url?: unknown }).url;
if (typeof candidate !== "string") {
  fail('the payload is missing a string "url" field');
}
if (!candidate.startsWith("https://")) {
  fail('the url field must start with "https://"');
}

// Ensure the output folder exists, then copy the bytes through unchanged.
try {
  mkdirSync(dropArea, { recursive: true });
  writeFileSync(`${dropArea}/POST.json`, rawBytes);
} catch (err) {
  fail(`could not write the output payload: ${String(err)}`);
}
