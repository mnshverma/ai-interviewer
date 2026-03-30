# Git Workflow — AI Interviewer

## Branch Strategy

- **`main`**: Production branch, always deployable, auto-deploys to Vercel
- **`feature/<name>`**: Feature branches for new features
- **`fix/<name>`**: Bug fix branches
- **`refactor/<name>`**: Refactoring branches

## Commit Convention

Use conventional commits:

```
<type>: <short description>

[optional body]
```

### Types
| Type | Use For |
|------|---------|
| `feat` | New feature or capability |
| `fix` | Bug fix |
| `refactor` | Code restructuring (no behavior change) |
| `style` | CSS/UI changes, formatting |
| `docs` | Documentation updates |
| `chore` | Build config, dependencies, tooling |
| `perf` | Performance improvement |

### Examples
```
feat: add interview history panel
fix: resolve camera permission error on Firefox
style: update glassmorphism effects on settings card
refactor: extract speech service into separate module
docs: update README with deployment instructions
chore: upgrade Vite to v7.2.4
```

## Git Rules

1. **Never** commit `.env` files (they're git-ignored)
2. **Never** commit `node_modules/` or `dist/`
3. **Always** run `npm run lint` before committing
4. **Always** run `npm run build` before pushing to main
5. **Keep** commits focused — one logical change per commit
6. **Write** descriptive commit messages (what & why, not just what)

## .gitignore Essentials
```
node_modules/
dist/
.env
.env.local
*.local
```
