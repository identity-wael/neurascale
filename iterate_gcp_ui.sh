#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Confirm current branch
CURRENT_BRANCH=$(git branch --show-current)
echo -e "${BLUE}🎯 Working on branch: ${GREEN}$CURRENT_BRANCH${NC}"

# Main prompt
PROMPT="You are working on the console app. You have an MCP browser with two pages open: one is localhost:3000 and the other is Google Cloud Platform. You need to clone/match the Google Cloud Platform UI on localhost:3000. Match the menu height, the spacing of text inside of the search, the curvature of the search box, the place where the text is placed same spacing, the color shape and dimensions of the search bar. The rest looks okay but your profile is a bit bigger make it smaller. Use the MCP Browser to compare both pages and verify your changes."

# Iteration loop
for i in {1..10}; do
    echo -e "\n${BLUE}=== Iteration $i of 10 ===${NC}"

    # Run Claude with the prompt
    claude --dangerously-skip-permissions "$PROMPT This is iteration $i of 10. When you finish making changes, evaluate what still needs to be adjusted."

    # Wait for file changes to complete
    sleep 5

    # Stage and commit changes
    git add -A
    git commit -m "feat(header-spacing): iteration $i - match GCP console UI elements"

    echo -e "${GREEN}✓ Committed to $CURRENT_BRANCH${NC}"
done

# Final evaluation
echo -e "\n${BLUE}=== FINAL EVALUATION ===${NC}"
claude --dangerously-skip-permissions "Final verification: Compare localhost:3000 with Google Cloud Platform in the MCP Browser. Check all elements: menu height, search box (spacing, curvature, text placement), search bar (color, shape, dimensions), and profile size. Is everything matching correctly now?"

# Final commit
sleep 3
git add -A
git commit -m "feat(header-spacing): final adjustments - GCP console UI match complete"

echo -e "\n${GREEN}✅ All 10 iterations complete!${NC}"
echo -e "📤 Ready to push: ${BLUE}git push origin $CURRENT_BRANCH${NC}"
