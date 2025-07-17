#!/usr/bin/env node

const { execFileSync } = require("child_process");

// Configuration
const NEON_PROJECT_ID = process.env.NEON_PROJECT_ID;
const GITHUB_TOKEN = process.env.GITHUB_TOKEN;
const GITHUB_REPOSITORY = process.env.GITHUB_REPOSITORY;
const DAYS_TO_KEEP = parseInt(process.env.DAYS_TO_KEEP || "7", 10);

// Helper function to execute commands safely
function exec(command, args = []) {
  try {
    // Use execFileSync instead of execSync to prevent command injection
    return execFileSync(command, args, { encoding: "utf8", shell: false });
  } catch (error) {
    console.error(`Command failed: ${command} ${args.join(" ")}`);
    console.error(error.message);
    return null;
  }
}

// Helper function to check if PR was merged
async function isPRMerged(prNumber) {
  try {
    const response = await fetch(
      `https://api.github.com/repos/${GITHUB_REPOSITORY}/pulls/${prNumber}`,
      {
        headers: {
          Authorization: `token ${GITHUB_TOKEN}`,
          Accept: "application/vnd.github.v3+json",
        },
      },
    );

    if (!response.ok) {
      console.error(`Failed to fetch PR #${prNumber}: ${response.status}`);
      return false;
    }

    const data = await response.json();
    return data.merged === true;
  } catch (error) {
    console.error(`Error checking PR #${prNumber}:`, error.message);
    return false;
  }
}

async function main() {
  console.log(
    `Starting cleanup of Neon branches older than ${DAYS_TO_KEEP} days...`,
  );
  console.log(`Project ID: ${NEON_PROJECT_ID}`);

  // Get all branches
  const branchesJson = exec("neonctl", [
    "branches",
    "list",
    "--project-id",
    NEON_PROJECT_ID,
    "-o",
    "json",
  ]);
  if (!branchesJson) {
    console.error("Failed to list branches");
    process.exit(1);
  }

  const branches = JSON.parse(branchesJson);
  console.log(`Found ${branches.length} total branches`);

  // Calculate cutoff date
  const cutoffDate = new Date();
  cutoffDate.setDate(cutoffDate.getDate() - DAYS_TO_KEEP);
  console.log(`Cutoff date: ${cutoffDate.toISOString()}`);

  let deletedCount = 0;
  let keptCount = 0;
  let skippedCount = 0;

  // Process each branch
  for (const branch of branches) {
    const { name, id, created_at } = branch;

    // Skip non-PR branches
    if (!name.match(/^preview\/pr-\d+/)) {
      console.log(`⏭️  Skipping non-PR branch: ${name}`);
      skippedCount++;
      continue;
    }

    // Extract PR number
    const prMatch = name.match(/preview\/pr-(\d+)/);
    if (!prMatch) {
      console.log(`⚠️  Could not extract PR number from: ${name}`);
      skippedCount++;
      continue;
    }

    const prNumber = prMatch[1];
    const branchDate = new Date(created_at);

    console.log(`\nProcessing: ${name} (PR #${prNumber})`);
    console.log(`  Created: ${branchDate.toISOString()}`);

    // Check if PR was merged
    const isMerged = await isPRMerged(prNumber);

    if (!isMerged) {
      console.log(`  ⏭️  PR #${prNumber} was not merged, keeping branch`);
      keptCount++;
      continue;
    }

    // Check if branch is old enough to delete
    if (branchDate >= cutoffDate) {
      console.log(
        `  ✅ PR #${prNumber} was merged but branch is recent, keeping for now`,
      );
      keptCount++;
      continue;
    }

    // Delete the branch
    console.log(`  🗑️  Deleting old merged PR branch...`);
    const deleteResult = exec("neonctl", [
      "branches",
      "delete",
      id,
      "--project-id",
      NEON_PROJECT_ID,
    ]);

    if (deleteResult) {
      console.log(`  ✅ Successfully deleted: ${name}`);
      deletedCount++;
    } else {
      console.log(`  ❌ Failed to delete: ${name}`);
    }
  }

  // Summary
  console.log("\n=== Cleanup Summary ===");
  console.log(`Total branches: ${branches.length}`);
  console.log(`Deleted: ${deletedCount}`);
  console.log(`Kept: ${keptCount}`);
  console.log(`Skipped: ${skippedCount}`);
  console.log("Cleanup completed!");
}

// Run the cleanup
main().catch((error) => {
  console.error("Cleanup failed:", error);
  process.exit(1);
});
