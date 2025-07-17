#!/bin/bash

# This script updates all remaining components to use Sanity content

echo "Updating Problem component..."
# Add import
sed -i '' "5i\\
import { useContent } from '@/src/contexts/ContentContext';
" components/sections/Problem.tsx

# Add hook usage
sed -i '' "/export default function Problem()/,/const containerRef/ s/const containerRef/const { problem } = useContent();\n  const containerRef/" components/sections/Problem.tsx

echo "Updating Roadmap component..."
# Add import
sed -i '' "5i\\
import { useContent } from '@/src/contexts/ContentContext';
" components/sections/Roadmap.tsx

# Add hook usage
sed -i '' "/export default function Roadmap()/,/const containerRef/ s/const containerRef/const { roadmap } = useContent();\n  const containerRef/" components/sections/Roadmap.tsx

echo "Updating Team component..."
# Add import
sed -i '' "5i\\
import { useContent } from '@/src/contexts/ContentContext';
" components/sections/Team.tsx

# Add hook usage
sed -i '' "/export default function Team()/,/const containerRef/ s/const containerRef/const { team } = useContent();\n  const containerRef/" components/sections/Team.tsx

echo "Updating Resources component..."
# Add import
sed -i '' "6i\\
import { useContent } from '@/src/contexts/ContentContext';
" components/sections/Resources.tsx

# Add hook usage
sed -i '' "/export default function Resources()/,/const containerRef/ s/const containerRef/const { resources } = useContent();\n  const containerRef/" components/sections/Resources.tsx

echo "Updating Contact component..."
# Add import
sed -i '' "6i\\
import { useContent } from '@/src/contexts/ContentContext';
" components/sections/Contact.tsx

# Add hook usage
sed -i '' "/export default function Contact()/,/const \[formData/ s/const \[formData/const { contact } = useContent();\n  const [formData/" components/sections/Contact.tsx

echo "All components updated!"
