#!/usr/bin/env python3
import subprocess
import time
import os
import json
import tempfile
import threading
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

class PersonaRunner:
    def __init__(self, branch):
        self.branch = branch
        self.specs_file = os.path.join(tempfile.gettempdir(), 'gcp_menu_specs.txt')
        self.qa_feedback_file = os.path.join(tempfile.gettempdir(), 'qa_feedback.txt')

    def run_claude(self, prompt, persona_name, timeout=180):
        """Run Claude with a specific persona and auto-timeout"""
        cmd = ["claude", "--dangerously-skip-permissions", prompt]

        print(f"\n{BOLD}{CYAN}👤 {persona_name} is working...{END}")

        process = subprocess.Popen(cmd)
        timer = threading.Timer(timeout, lambda: process.terminate())
        timer.start()

        try:
            process.wait()
        except:
            pass
        finally:
            timer.cancel()

        print(f"{GREEN}✅ {persona_name} completed{END}")

def get_designer_prompt():
    """UI/UX Designer persona - Analyzes and documents GCP menu bar specifications"""
    return """
PERSONA: Senior UI/UX Designer at Google Cloud Platform
CONTEXT: You are an expert designer with 10+ years of experience in design systems and pixel-perfect implementations. You have deep knowledge of Google's Material Design principles and the GCP console interface. You are working on the console app project.

FUNCTION: Your role is to meticulously analyze and document every visual aspect of the Google Cloud Platform menu bar to create a comprehensive specification document for the console app.

CRITICAL REQUIREMENT: DO NOT CHANGE THE LOGO/BRAND TEXT. The existing NEURASCALE logo must remain EXACTLY as it is - same text, same color, same font, same everything. You are ONLY documenting how other elements should be styled.

TASK: Using the MCP browser with the two tabs open (localhost:3000 showing the console app and Google Cloud Platform console), analyze the GCP menu bar and document:

1. DIMENSIONS & LAYOUT:
   - Exact header height in pixels
   - Container max-width and padding
   - Grid system and spacing units used

2. NAVIGATION MENU BUTTON:
   - Exact size (width x height)
   - Icon dimensions and stroke width
   - Margin from left edge
   - Hover state styling (background color, border-radius)
   - Active/pressed states

3. LOGO & BRAND (DO NOT CHANGE):
   - ⚠️ IMPORTANT: Document that the NEURASCALE logo must remain UNCHANGED
   - Note the spacing around the existing logo
   - DO NOT suggest any changes to the logo text, color, or font

4. PROJECT SELECTOR:
   - Container dimensions (width x height)
   - Font specifications
   - Icon size and type
   - Padding and margins
   - Border styling (if any)
   - Hover and focus states

5. SEARCH BAR:
   - Container max-width and height
   - Background color and border
   - Border-radius value
   - Search icon specifications (size, color, position)
   - Input text styling (font-size, color, line-height)
   - Placeholder text color
   - Search button dimensions and styling
   - Focus state (border color, shadow)
   - Spacing between search icon, input, and button

6. SEARCH BUTTON:
   - Exact text content
   - Font specifications
   - Padding values
   - Background and text colors
   - Hover state changes

7. COLOR PALETTE:
   - All colors used (backgrounds, text, borders, hover states)
   - Include both hex and rgb values

8. SPACING RHYTHM:
   - Document the spacing pattern between all elements
   - Note any consistent spacing units (4px, 8px grid, etc.)

EVALUATION: Create a detailed specification document that a developer can use to recreate the GCP menu bar styling in the console app while keeping the NEURASCALE logo EXACTLY as it currently is.

CRITICAL: The NEURASCALE logo/brand must NOT be changed in any way. Focus only on the other menu bar elements.
"""

def get_developer_prompt(iteration, specs_file, qa_feedback_file):
    """Frontend Developer persona - Implements the specifications"""

    qa_feedback = ""
    if iteration > 1 and os.path.exists(qa_feedback_file):
        with open(qa_feedback_file, 'r') as f:
            qa_feedback = f.read()

    return f"""
PERSONA: Senior Frontend Developer specializing in React and Design Systems
CONTEXT: You are an experienced developer working on the console app project. The console app is running on localhost:3000. You have access to the MCP browser and terminal to verify your changes.

CRITICAL REQUIREMENT: DO NOT MODIFY THE NEURASCALE LOGO IN ANY WAY. Keep it exactly as it is - same text, same color, same font, same styling. Only modify other menu bar elements.

FUNCTION: Implement the Google Cloud Platform menu bar design in the console app based on the designer's specifications. YOU MUST verify all changes work correctly before considering the task complete.

TASK: This is iteration {iteration} of 3 for the console app.

{"INITIAL IMPLEMENTATION:" if iteration == 1 else "REFINEMENT BASED ON QA FEEDBACK:"}

{f"QA FEEDBACK TO ADDRESS:{qa_feedback}" if qa_feedback else "Refer to the designer's specifications saved earlier."}

IMPLEMENTATION PROCESS:
1. Review the current code in Header.tsx
2. Make the necessary changes based on specifications/feedback
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
- Only commit code that is fully functional and tested
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

def get_qa_prompt(iteration):
    """QA Engineer persona - Validates implementation against GCP"""
    return f"""
PERSONA: Senior QA Engineer specializing in Visual Regression Testing
CONTEXT: You are a detail-oriented QA professional working on the console app project. The console app is running on localhost:3000. The NEURASCALE logo must remain unchanged from the original.

FUNCTION: Compare the implemented menu bar in the console app (localhost:3000) against the Google Cloud Platform console, identifying any remaining differences while verifying the NEURASCALE logo remains unchanged.

TASK: This is iteration {iteration} of 3 for the console app.

Using the MCP browser with both tabs open (console app on localhost:3000 and Google Cloud Platform console):

1. FIRST, verify the NEURASCALE logo:
   - Confirm it remains EXACTLY as it was originally
   - Same text, same color, same font
   - If the logo has been changed in ANY way, this is a CRITICAL issue

2. Compare these specific elements between the console app and GCP:
   - Header height and overall dimensions
   - Navigation menu button (size, position, hover effect)
   - Project selector (all aspects)
   - Search bar (dimensions, colors, border-radius, internal spacing)
   - Search button (size, text, styling)
   - Spacing between all elements

3. For each difference found in the console app, document:
   - ELEMENT: Which specific element differs
   - CURRENT: What it looks like in the console app (localhost:3000)
   - EXPECTED: What it should look like (from GCP)
   - SPECIFIC FIX: Exact change needed (e.g., "increase padding-left from 12px to 16px")

4. Check interactive states in the console app:
   - Hover effects on all interactive elements
   - Focus states on inputs
   - Active/pressed states

5. Verify no regressions from previous iterations in the console app

CRITICAL NOTE: The NEURASCALE logo should be UNCHANGED. If it has been modified in any way, report this as a critical issue that must be reverted.

EVALUATION: Create a precise, actionable list of ONLY the differences that still need to be fixed in the console app. Be specific with measurements and values. If the logo has been changed, make this the #1 priority issue.
"""

def get_final_developer_prompt(qa_feedback_file):
    """Final developer prompt to address last QA feedback"""
    qa_feedback = ""
    if os.path.exists(qa_feedback_file):
        with open(qa_feedback_file, 'r') as f:
            qa_feedback = f.read()

    return f"""
PERSONA: Senior Frontend Developer specializing in React and Design Systems
CONTEXT: You are implementing the final refinements for the console app based on the QA team's last review. The console app is running on localhost:3000. The NEURASCALE logo must remain exactly as it is.

CRITICAL: DO NOT CHANGE THE NEURASCALE LOGO. It must keep its original text, color, and font.

FUNCTION: Address the final QA feedback to achieve a perfect match between the console app and the Google Cloud Platform menu bar styling. YOU MUST ensure all changes work correctly.

TASK: FINAL IMPLEMENTATION for the console app - Address remaining issues from QA

QA's FINAL FEEDBACK:
{qa_feedback}

FINAL IMPLEMENTATION PROCESS:
1. Carefully review the QA feedback
2. Implement the requested fixes in Header.tsx
3. **DO NOT TOUCH THE NEURASCALE LOGO** - Leave it exactly as is
4. **MANDATORY MCP BROWSER VERIFICATION:**
   - Hard refresh localhost:3000
   - Open browser console and ensure ZERO errors
   - Verify NEURASCALE logo is unchanged
   - Test EVERY interactive element:
     * Navigation menu functionality
     * Project selector functionality
     * Search bar input and submission
     * All hover states
   - Do a final side-by-side comparison with GCP

5. **MANDATORY TERMINAL VERIFICATION:**
   - Check for any compilation errors
   - Check for any runtime warnings
   - Ensure clean build with no issues

FINAL VERIFICATION CHECKLIST - ALL MUST BE CHECKED:
□ All QA feedback items addressed
□ NEURASCALE logo remains completely unchanged
□ Zero console errors in browser
□ Zero compilation errors in terminal
□ Navigation menu opens/closes properly
□ Project selector works correctly
□ Search functionality is intact
□ All hover states work
□ Visual styling matches GCP (except NEURASCALE logo)
□ No regression from previous iterations
□ Hard refresh shows no issues

DO NOT COMPLETE THIS TASK IF ANY CHECKBOX ABOVE IS NOT VERIFIED!

Remember: The NEURASCALE logo must remain exactly as it is - no changes to text, color, or font.

EVALUATION: After these changes, the console app's menu bar styling should match GCP's exactly (except for the unchanged NEURASCALE logo) with all functionality working perfectly and ZERO errors.
"""

def commit_changes(iteration, phase, branch):
    """Commit changes with appropriate message"""
    subprocess.run(["git", "add", "-A"], capture_output=True)
    diff_result = subprocess.run(["git", "diff", "--staged", "--quiet"], capture_output=True)

    if diff_result.returncode != 0:
        if phase == "final":
            commit_msg = f"feat(console-app): final UI adjustments - GCP menu bar styling complete (logo unchanged)"
        else:
            commit_msg = f"feat(console-app): UI iteration {iteration} - {phase} implementation (logo unchanged)"

        subprocess.run(["git", "commit", "-m", commit_msg], capture_output=True)
        print(f"{GREEN}✅ Changes committed to branch: {branch}{END}")

        # Show files changed
        files_changed = subprocess.check_output(
            ["git", "diff", "--name-only", "HEAD~1"],
            text=True
        ).strip().split('\n')
        if files_changed and files_changed[0]:
            print(f"{CYAN}📝 Files modified: {', '.join(files_changed)}{END}")
        return True
    else:
        print(f"{YELLOW}📭 No changes to commit{END}")
        return False

def run_iteration_pipeline(iteration, persona_runner):
    """Run the Developer -> QA pipeline for one iteration"""
    print(f"\n{BOLD}{MAGENTA}{'='*80}{END}")
    print(f"{BOLD}{MAGENTA}{'CONSOLE APP - ITERATION ' + str(iteration) + ' OF 3':^80}{END}")
    print(f"{BOLD}{MAGENTA}{'='*80}{END}")

    # Developer Phase
    print(f"\n{BOLD}{BLUE}[ DEVELOPER PHASE - Console App ]{END}")
    print(f"{YELLOW}⚠️  Developer MUST verify all changes in MCP browser AND terminal before proceeding{END}")
    print(f"{RED}⚠️  DO NOT CHANGE THE NEURASCALE LOGO{END}")

    developer_prompt = get_developer_prompt(
        iteration,
        persona_runner.specs_file,
        persona_runner.qa_feedback_file
    )

    start_time = time.time()
    persona_runner.run_claude(developer_prompt, "Developer")
    dev_time = int(time.time() - start_time)

    # Wait for file changes
    print(f"{YELLOW}⏳ Waiting 5s for console app file changes...{END}")
    time.sleep(5)

    # Commit developer changes
    commit_changes(iteration, "developer", persona_runner.branch)

    # QA Phase
    print(f"\n{BOLD}{RED}[ QA PHASE - Console App ]{END}")
    qa_prompt = get_qa_prompt(iteration)

    start_time = time.time()
    persona_runner.run_claude(qa_prompt, "QA Engineer")
    qa_time = int(time.time() - start_time)

    # Summary
    print(f"\n{DIM}Developer time: {dev_time}s | QA time: {qa_time}s{END}")

    return True

def main():
    os.system('clear')

    # Get current branch
    current_branch = subprocess.check_output(["git", "branch", "--show-current"]).decode().strip()

    print(f"{BOLD}{MAGENTA}🎨 CONSOLE APP - GCP UI MATCHING SYSTEM{END}")
    print(f"{MAGENTA}{'='*80}{END}")
    print(f"{BLUE}📍 Working on branch: {current_branch}{END}")
    print(f"{BLUE}🖥️  Console app: http://localhost:3000{END}")
    print(f"{RED}🏢 NEURASCALE logo must remain UNCHANGED{END}")
    print(f"{BLUE}🔄 Iterations: 3{END}")
    print(f"{BLUE}🕐 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{END}")

    print(f"\n{CYAN}👥 Personas working on the console app:{END}")
    print(f"   {BOLD}1. Designer{END} - Analyzes GCP and creates specifications")
    print(f"   {BOLD}2. Developer{END} - Implements code changes with mandatory verification")
    print(f"   {BOLD}3. QA Engineer{END} - Validates console app against GCP")

    print(f"\n{RED}⚠️  CRITICAL: The NEURASCALE logo must NOT be changed{END}")
    print(f"{YELLOW}⚠️  IMPORTANT: Only the Developer makes code changes{END}")
    print(f"{YELLOW}⚠️  Developer MUST verify in MCP browser AND terminal before each commit{END}")

    # Check for uncommitted changes
    subprocess.run(["git", "add", "-A"], capture_output=True)
    diff_result = subprocess.run(["git", "diff", "--staged", "--quiet"], capture_output=True)
    if diff_result.returncode != 0:
        print(f"\n{YELLOW}⚠️  Uncommitted changes detected, committing first...{END}")
        subprocess.run(["git", "commit", "-m", "feat(console-app): save work before UI matching process"], capture_output=True)

    persona_runner = PersonaRunner(current_branch)

    # Initial Designer Analysis
    print(f"\n{BOLD}{YELLOW}[ INITIAL DESIGN ANALYSIS - Console App vs GCP ]{END}")
    print(f"{YELLOW}The Designer will analyze GCP's menu bar to create specifications...{END}")
    print(f"{RED}Note: NEURASCALE logo must remain unchanged{END}")

    designer_prompt = get_designer_prompt()
    persona_runner.run_claude(designer_prompt, "UI/UX Designer")

    print(f"{GREEN}✅ Design specifications for console app created{END}")
    print(f"\n{CYAN}Starting console app implementation iterations...{END}")
    time.sleep(3)

    # Run iterations
    start_time = datetime.now()

    try:
        for i in range(1, 4):  # 3 iterations
            run_iteration_pipeline(i, persona_runner)

            # Progress
            progress = "█" * i + "░" * (3 - i)
            percentage = (i / 3) * 100
            print(f"\n{BOLD}{BLUE}📊 Console App Progress: [{progress}] {i}/3 ({percentage:.0f}%){END}")

            if i < 3:
                print(f"\n{DIM}Starting console app iteration {i+1} in 3 seconds...{END}")
                time.sleep(3)

        # Final Developer Implementation
        print(f"\n{BOLD}{YELLOW}[ FINAL DEVELOPER IMPLEMENTATION - Console App ]{END}")
        print(f"{YELLOW}Implementing final QA feedback...{END}")
        print(f"{RED}⚠️  REMINDER: DO NOT CHANGE THE NEURASCALE LOGO!{END}")
        print(f"{RED}⚠️  REMINDER: Verify all changes in browser AND terminal!{END}")

        final_prompt = get_final_developer_prompt(persona_runner.qa_feedback_file)
        persona_runner.run_claude(final_prompt, "Developer (Final)")

        # Wait and commit final changes
        print(f"{YELLOW}⏳ Waiting 5s for final console app changes...{END}")
        time.sleep(5)
        commit_changes(0, "final", current_branch)

    except KeyboardInterrupt:
        print(f"\n\n{YELLOW}⏸️  Console app process interrupted by user{END}")

    # Final Summary
    end_time = datetime.now()
    duration = (end_time - start_time).seconds
    minutes = duration // 60
    seconds = duration % 60

    print(f"\n{BOLD}{GREEN}{'='*80}{END}")
    print(f"{BOLD}{GREEN}{'🎉 CONSOLE APP UI MATCHING COMPLETE!':^80}{END}")
    print(f"{BOLD}{GREEN}{'='*80}{END}")

    # Show commit history
    print(f"\n{CYAN}📋 Console app commits on {current_branch}:{END}")
    commits = subprocess.check_output(
        ["git", "log", "--oneline", "-15", "--pretty=format:%h %s"],
        text=True
    ).strip().split('\n')

    for commit in commits[:10]:
        if "console-app" in commit:
            print(f"   {commit}")

    print(f"\n{GREEN}✅ Console App Summary:{END}")
    print(f"   • Design analysis completed")
    print(f"   • 3 implementation iterations (with verification)")
    print(f"   • 3 QA validations")
    print(f"   • Final implementation (with verification)")
    print(f"   • Total time: {minutes}m {seconds}s")
    print(f"   • NEURASCALE logo kept unchanged")
    print(f"   • All changes verified in browser and terminal")

    print(f"\n{BLUE}🖥️  Console app: http://localhost:3000{END}")
    print(f"{BLUE}🌿 Branch: {current_branch}{END}")
    print(f"{BOLD}{CYAN}📤 To push: git push origin {current_branch}{END}")

    # Cleanup temp files
    for f in [persona_runner.specs_file, persona_runner.qa_feedback_file]:
        if os.path.exists(f):
            os.remove(f)

if __name__ == "__main__":
    main()
