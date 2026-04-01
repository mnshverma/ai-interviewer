# Git Workflow — AI Interviewer

## Branch Strategy

- **`main`**: Production branch, always deployable
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
feat: add device test workflow
fix: resolve form validation error
style: update dark theme colors
refactor: simplify session state initialization
docs: update AGENTS.md
chore: upgrade pypdf dependency
```

## Git Rules

1. **Never** commit `.env` files (they're git-ignored)
2. **Never** commit `__pycache__/` or `.pyc` files
3. **Always** run `python -m py_compile app.py` before committing
4. **Keep** commits focused — one logical change per commit
5. **Write** descriptive commit messages (what & why, not just what)

## .gitignore Essentials
```
.env
.env.local
__pycache__/
*.pyc
*.pyo
.pytest_cache/
streamlit/
.venv/
venv/
```

## Pre-commit Check
```bash
# Verify Python syntax
python -m py_compile app.py
```