# Contributing to NeuraScale

Thank you for your interest in contributing to NeuraScale! We welcome contributions from the community and are grateful for any help you can provide.

## Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct:

- Be respectful and inclusive
- Welcome newcomers and help them get started
- Focus on constructive criticism
- Respect differing viewpoints and experiences

## How to Contribute

### Reporting Bugs

1. **Check existing issues** to avoid duplicates
2. **Use the bug report template**
3. **Include**:
   - Clear description
   - Steps to reproduce
   - Expected vs actual behavior
   - Screenshots if applicable
   - Environment details

### Suggesting Features

1. **Check the roadmap** first
2. **Open a discussion** before creating an issue
3. **Provide**:
   - Use case explanation
   - Proposed solution
   - Alternative approaches
   - Mockups/examples if possible

### Contributing Code

#### 1. Fork and Clone

```bash
# Fork on GitHub, then:
git clone https://github.com/YOUR_USERNAME/neurascale.git
cd neurascale
git remote add upstream https://github.com/identity-wael/neurascale.git
```

#### 2. Create a Branch

```bash
# Update main branch
git checkout main
git pull upstream main

# Create feature branch
git checkout -b feature/your-feature-name
```

Branch naming conventions:

- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation
- `refactor/` - Code refactoring
- `test/` - Test improvements

#### 3. Set Up Development Environment

```bash
# Navigate to web app
cd apps/web

# Install dependencies
npm install

# Copy environment variables
cp .env.example .env.local

# Start development
npm run dev
```

#### 4. Make Your Changes

- Follow existing code style
- Write meaningful commit messages
- Add tests for new features
- Update documentation as needed

#### 5. Commit Guidelines

We use conventional commits:

```bash
# Format
<type>(<scope>): <subject>

# Examples
feat(sanity): add new content schema
fix(ui): resolve button alignment issue
docs(readme): update setup instructions
```

Types:

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Test changes
- `chore`: Build/tool changes

#### 6. Test Your Changes

```bash
# Run tests
npm test

# Type checking
npm run type-check

# Linting
npm run lint

# Format code
npm run format
```

#### 7. Submit Pull Request

1. Push your branch:

   ```bash
   git push origin feature/your-feature-name
   ```

2. Open PR on GitHub
3. Fill out PR template
4. Link related issues
5. Wait for review

### Pull Request Guidelines

#### PR Title Format

```
<type>(<scope>): <description>

# Examples
feat(cms): implement blog content type
fix(auth): resolve session timeout issue
```

#### PR Description Should Include

- **What**: Brief description of changes
- **Why**: Motivation and context
- **How**: Technical approach
- **Testing**: How you tested changes
- **Screenshots**: For UI changes
- **Breaking Changes**: If any

#### PR Checklist

- [ ] Code follows project style guide
- [ ] Tests pass locally
- [ ] Documentation updated
- [ ] No console errors/warnings
- [ ] Responsive design maintained
- [ ] Accessibility considered
- [ ] Performance impact assessed

## Development Guidelines

### Code Style

#### TypeScript

```typescript
// Use explicit types
interface UserProps {
  name: string;
  email: string;
  role?: "admin" | "user";
}

// Prefer const assertions
const ROLES = ["admin", "user"] as const;

// Use proper naming
const getUserById = async (id: string): Promise<User> => {
  // Implementation
};
```

#### React Components

```typescript
// Functional components with TypeScript
interface ButtonProps {
  variant?: 'primary' | 'secondary'
  onClick?: () => void
  children: React.ReactNode
}

export function Button({
  variant = 'primary',
  onClick,
  children
}: ButtonProps) {
  return (
    <button
      className={cn('btn', `btn-${variant}`)}
      onClick={onClick}
    >
      {children}
    </button>
  )
}
```

#### File Organization

```
components/
├── ui/                 # Reusable UI components
├── sections/          # Page sections
├── layout/           # Layout components
└── common/           # Shared components
```

### Testing Guidelines

#### Unit Tests

```typescript
// Button.test.tsx
import { render, screen } from '@testing-library/react'
import { Button } from './Button'

describe('Button', () => {
  it('renders children correctly', () => {
    render(<Button>Click me</Button>)
    expect(screen.getByText('Click me')).toBeInTheDocument()
  })
})
```

#### Integration Tests

```typescript
// api.test.ts
describe("API Routes", () => {
  it("returns correct response", async () => {
    const response = await fetch("/api/test");
    const data = await response.json();
    expect(data).toEqual({ success: true });
  });
});
```

### Documentation Standards

#### Code Comments

```typescript
/**
 * Fetches user data from the API
 * @param userId - The unique user identifier
 * @returns Promise resolving to user data
 * @throws {Error} If user not found
 */
async function getUser(userId: string): Promise<User> {
  // Implementation
}
```

#### README Updates

- Keep examples current
- Update screenshots
- Document new features
- Include migration guides

## Review Process

### What We Look For

1. **Code Quality**

   - Clean, readable code
   - Proper error handling
   - Performance considerations
   - Security best practices

2. **Testing**

   - Adequate test coverage
   - Edge cases handled
   - No broken existing tests

3. **Documentation**

   - Code comments where needed
   - README updates
   - API documentation

4. **UI/UX**
   - Consistent design
   - Responsive layout
   - Accessibility compliance
   - Smooth animations

### Review Timeline

- Initial review: 2-3 business days
- Follow-up reviews: 1-2 business days
- Complex PRs may take longer

## Getting Help

### Resources

- [Project Documentation](./docs)
- [Discord Community](#)
- [GitHub Discussions](https://github.com/identity-wael/neurascale/discussions)

### Asking Questions

1. Search existing issues/discussions
2. Provide context and code examples
3. Be specific about the problem
4. Share error messages/logs

## Recognition

Contributors will be:

- Listed in our README
- Mentioned in release notes
- Invited to contributor meetings
- Given credit in presentations

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to NeuraScale! 🚀
