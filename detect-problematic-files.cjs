const fs = require("fs");
const path = require("path");

const ROOT = process.cwd();
const MAX_PATH_LENGTH = 250; // Windows safe limit
let issues = [];

function scanDir(dir) {
  const items = fs.readdirSync(dir);

  for (const item of items) {
    const fullPath = path.join(dir, item);
    const stats = fs.statSync(fullPath);

    // Detect long path names
    if (fullPath.length > MAX_PATH_LENGTH) {
      issues.push({
        type: "LONG_PATH",
        path: fullPath,
        length: fullPath.length
      });
    }

    // Detect weird filenames
    if (/[^a-zA-Z0-9._/-]/.test(item)) {
      issues.push({
        type: "WEIRD_CHARACTERS",
        path: fullPath
      });
    }

    // Detect PDF or temp files in testsprite folders
    if (fullPath.includes("testsprite_tests/tmp") && fullPath.endsWith(".pdf")) {
      issues.push({
        type: "TMP_PDF_FILE",
        path: fullPath
      });
    }

    if (stats.isDirectory()) {
      scanDir(fullPath);
    }
  }
}

console.log("🔍 Scanning project for problematic files...\n");
scanDir(ROOT);

if (issues.length === 0) {
  console.log("✅ All good! No problematic files detected.");
} else {
  console.log(`⚠️ Found ${issues.length} problematic files:\n`);
  issues.forEach((issue, index) => {
    console.log(
      `${index + 1}. [${issue.type}] (${issue.path.length || ""}) → ${issue.path}`
    );
  });
  console.log("\n💡 Suggestion: Fix or add them to .gitignore");
}
