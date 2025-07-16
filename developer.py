#!/usr/bin/env python3
import subprocess
import time
import os
import sys
from datetime import datetime

# Colors
BLUE = '\033[94m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
MAGENTA = '\033[95m'
CYAN = '\033[96m'
BOLD = '\033[1m'
DIM = '\033[2m'
END = '\033[0m'

def get_developer_prompt(specs_content):
    """Frontend Developer prompt with specifications"""

    return f"""
PERSONA: Senior Frontend Developer specializing in React and Design Systems
CONTEXT: You are an experienced developer working on the console app project. The console app is running on localhost:3000. You have access to the MCP browser and terminal to verify your changes.

CRITICAL REQUIREMENT: DO NOT MODIFY THE NEURASCALE LOGO IN ANY WAY. Keep it exactly as it is - same text, same color, same font, same styling. Only modify other menu bar elements.

FUNCTION: Implement the Google Cloud Platform menu bar design in the console app based on the provided specifications. YOU MUST verify all changes work correctly before considering the task complete.

SPECIFICATIONS PROVIDED:
{specs_content}

IMPLEMENTATION PROCESS:
1. Review the current code in Header.tsx
2. Implement changes based on the specifications above
3. **MANDATORY VERIFICATION IN MCP BROWSER:**
   - Refresh localhost:3000
   - Open browser console (F12) and check for ANY errors
   - If there are errors, fix them before proceeding
   - Verify the visual changes match expectations
   - Test ALL interactive elements:
     * Click the navigation menu button - ensure it opens/closes
     * Click the project selector - ensure dropdown works
     * Type in the search bar - ensure it accepts input
     * Click the search button - ensure it responds
     * Test ALL hover states on modified elements
   - Compare side-by-side with Google Cloud Platform

4. **MANDATORY TERMINAL VERIFICATION:**
   - Check the terminal where the app is running
   - Ensure there are NO compilation errors
   - Ensure there are NO runtime warnings related to your changes
   - If there are issues, fix them before proceeding

5. **FUNCTIONALITY CHECKLIST - YOU MUST VERIFY EACH:**
   □ Navigation menu opens and closes properly
   □ Project selector dropdown functions correctly
   □ Search input accepts text
   □ Search functionality triggers on button click/enter
   □ All hover effects work on modified elements
   □ No console errors in browser
   □ No terminal errors or warnings
   □ Page loads without issues
   □ All existing features still work
   □ NEURASCALE logo remains unchanged

CHANGES TO IMPLEMENT:
1. Update the header container height and padding to match GCP
2. Adjust the navigation menu button (Menu icon) - size, positioning, hover effects
3. **DO NOT CHANGE THE NEURASCALE LOGO** - Leave it exactly as it is
4. Implement the project selector with exact GCP styling
5. Create the search bar with precise dimensions, colors, and states
6. Add the search button with proper styling
7. Ensure all hover states match GCP exactly
8. Apply the correct color values throughout (except logo)
9. Match the spacing rhythm between elements

CRITICAL REQUIREMENTS:
- **DO NOT MODIFY THE NEURASCALE LOGO/TEXT** - No color, font, or style changes
- **DO NOT PROCEED** if there are any errors in browser console
- **DO NOT PROCEED** if there are any compilation errors in terminal
- **DO NOT PROCEED** if any functionality is broken
- Only complete when code is fully functional and tested
- Take time to thoroughly test - quality over speed

BEFORE COMPLETING - FINAL VERIFICATION:
1. Hard refresh localhost:3000 (Ctrl+Shift+R or Cmd+Shift+R)
2. Open browser console and confirm: "No errors present"
3. Verify NEURASCALE logo is unchanged
4. Test every interactive element one more time
5. Check terminal for any warnings/errors
6. Only then consider your implementation complete

EVALUATION: Your implementation should match GCP's menu bar styling exactly while keeping the NEURASCALE logo completely unchanged and ensuring 100% functionality with zero errors.
"""

def run_developer():
    """Run the developer implementation"""

    # Check if specification file exists
    spec_file = "gcp-menubar-specification.md"
    if not os.path.exists(spec_file):
        print(f"{RED}❌ Error: Specification file '{spec_file}' not found!{END}")
        print(f"{YELLOW}Please ensure '{spec_file}' is in the same directory as this script.{END}")
        sys.exit(1)

    # Read specifications
    try:
        with open(spec_file, 'r') as f:
            specs_content = f.read()
        print(f"{GREEN}✅ Loaded specifications from '{spec_file}'{END}")
    except Exception as e:
        print(f"{RED}❌ Error reading specification file: {e}{END}")
        sys.exit(1)

    # Get current branch
    current_branch = subprocess.check_output(["git", "branch", "--show-current"]).decode().strip()

    # Clear screen
    os.system('clear')

    print(f"{BOLD}{MAGENTA}🎨 CONSOLE APP - DEVELOPER IMPLEMENTATION{END}")
    print(f"{MAGENTA}{'='*80}{END}")
    print(f"{BLUE}📍 Working on branch: {current_branch}{END}")
    print(f"{BLUE}🖥️  Console app: http://localhost:3000{END}")
    print(f"{BLUE}📄 Specification file: {spec_file}{END}")
    print(f"{RED}🏢 NEURASCALE logo must remain UNCHANGED{END}")
    print(f"{BLUE}🕐 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{END}")

    print(f"\n{YELLOW}⚠️  IMPORTANT REMINDERS:{END}")
    print(f"{YELLOW}   • DO NOT change the NEURASCALE logo{END}")
    print(f"{YELLOW}   • Verify ALL changes in MCP browser{END}")
    print(f"{YELLOW}   • Check terminal for compilation errors{END}")
    print(f"{YELLOW}   • Test ALL interactive elements{END}")
    print(f"{YELLOW}   • Only proceed when everything works{END}")

    # Check for uncommitted changes
    subprocess.run(["git", "add", "-A"], capture_output=True)
    diff_result = subprocess.run(["git", "diff", "--staged", "--quiet"], capture_output=True)
    if diff_result.returncode != 0:
        print(f"\n{YELLOW}⚠️  Uncommitted changes detected, committing first...{END}")
        subprocess.run(["git", "commit", "-m", "feat(console-app): save work before developer implementation"], capture_output=True)

    # Prepare prompt
    developer_prompt = get_developer_prompt(specs_content)

    print(f"\n{BOLD}{BLUE}[ STARTING DEVELOPER IMPLEMENTATION ]{END}")
    print(f"{CYAN}The developer will now implement the GCP menu bar styling based on specifications...{END}")
    print(f"{RED}Remember: Keep NEURASCALE logo unchanged!{END}\n")

    # Run Claude
    cmd = ["claude", "--dangerously-skip-permissions", developer_prompt]

    start_time = time.time()
    print(f"{BOLD}{CYAN}👤 Developer is working...{END}")

    # Run the command
    result = subprocess.run(cmd)

    elapsed = int(time.time() - start_time)
    print(f"\n{GREEN}✅ Developer completed (took {elapsed}s){END}")

    # Wait for file changes
    print(f"{YELLOW}⏳ Waiting 5s for file changes to complete...{END}")
    time.sleep(5)

    # Commit changes
    subprocess.run(["git", "add", "-A"], capture_output=True)
    diff_result = subprocess.run(["git", "diff", "--staged", "--quiet"], capture_output=True)

    if diff_result.returncode != 0:
        commit_msg = "feat(console-app): implement GCP menu bar styling (logo unchanged)"
        subprocess.run(["git", "commit", "-m", commit_msg], capture_output=True)
        print(f"{GREEN}✅ Changes committed to branch: {current_branch}{END}")

        # Show files changed
        files_changed = subprocess.check_output(
            ["git", "diff", "--name-only", "HEAD~1"],
            text=True
        ).strip().split('\n')
        if files_changed and files_changed[0]:
            print(f"{CYAN}📝 Files modified: {', '.join(files_changed)}{END}")
    else:
        print(f"{YELLOW}📭 No changes to commit{END}")

    # Final summary
    print(f"\n{BOLD}{GREEN}{'='*80}{END}")
    print(f"{BOLD}{GREEN}{'🎉 DEVELOPER IMPLEMENTATION COMPLETE!':^80}{END}")
    print(f"{BOLD}{GREEN}{'='*80}{END}")

    print(f"\n{GREEN}✅ Summary:{END}")
    print(f"   • Specifications loaded from: {spec_file}")
    print(f"   • Implementation completed")
    print(f"   • Changes verified and committed")
    print(f"   • NEURASCALE logo kept unchanged")

    print(f"\n{CYAN}📋 Next steps:{END}")
    print(f"   1. Test the implementation at http://localhost:3000")
    print(f"   2. Verify all functionality works correctly")
    print(f"   3. Compare with Google Cloud Platform console")

    print(f"\n{BLUE}🖥️  Console app: http://localhost:3000{END}")
    print(f"{BLUE}🌿 Branch: {current_branch}{END}")
    print(f"{BOLD}{CYAN}📤 To push: git push origin {current_branch}{END}\n")

if __name__ == "__main__":
    try:
        run_developer()
    except KeyboardInterrupt:
        print(f"\n\n{YELLOW}⏸️  Process interrupted by user{END}")
        sys.exit(0)
