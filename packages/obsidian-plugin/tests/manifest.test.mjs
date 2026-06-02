import fs from "node:fs";
import path from "node:path";
import test from "node:test";
import assert from "node:assert/strict";

test("plugin manifest exists and has an id", () => {
  const manifestPath = path.resolve("manifest.json");
  const manifest = JSON.parse(fs.readFileSync(manifestPath, "utf8"));
  assert.equal(typeof manifest.id, "string");
  assert.ok(manifest.id.length > 0);
});
