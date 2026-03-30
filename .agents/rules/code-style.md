# Code Style — AI Interviewer

## Language & Framework
- **JavaScript** (ES2022+), no TypeScript
- **React 19** with functional components only
- **Vite 7** for build tooling
- **Vanilla CSS** — no Tailwind, no CSS-in-JS

## React Conventions

### Components
- One component per file
- Use `.jsx` extension for all React files
- Export as `default export`
- Name files in PascalCase matching the component name
- Place all components in `src/components/`

### Hooks
- Use `useState` for local state (no Redux, no Context API)
- Use `useCallback` for memoized event handlers
- Use `useEffect` with proper cleanup functions
- Use `useRef` for DOM refs and mutable values that don't trigger re-renders
- Always specify dependency arrays for `useEffect` and `useCallback`

### Props
- Destructure props in function signature
- Use descriptive prop names
- Document complex props with comments
- No PropTypes required (keep it simple)

### State Management
- All global interview state lives in `App.jsx`
- Pass state down as props
- Pass setters down as callback props
- Use lifting state up pattern — never duplicate state across components

## Naming Conventions

| Entity | Convention | Example |
|--------|-----------|---------|
| Components | PascalCase | `VideoInterview.jsx` |
| Functions | camelCase | `handleStartInterview()` |
| Event handlers | `handle` prefix | `handleSubmitAnswer()` |
| Constants | UPPER_SNAKE_CASE | `MAX_QUESTIONS` |
| CSS classes | kebab-case | `.interview-container` |
| CSS variables | `--` prefix, kebab-case | `--primary-blue` |
| Files (non-components) | camelCase | `openRouterAPI.js` |

## CSS Rules
- All styles in `src/index.css` (single design system file)
- Use CSS custom properties for theming (colors, spacing, radii, shadows)
- Use glassmorphism effects (backdrop-filter, translucent backgrounds)
- No inline styles in JSX
- Use `rem` for sizing, `px` only for borders/shadows
- Mobile-first responsive design with media queries
- Smooth transitions on interactive elements (0.2-0.3s ease)

## File Organization
```
src/
├── App.jsx              ← Orchestrator only, state + flow logic
├── main.jsx             ← Entry point, never modify
├── index.css            ← ALL styles, design system tokens
├── components/          ← One component per file
│   └── *.jsx
└── utils/               ← Pure logic, no React
    └── *.js
```

## Code Quality
- No `console.log` in production code (use only for dev debugging, remove before commit)
- No `var` — use `const` by default, `let` only when reassignment is needed
- Use template literals over string concatenation
- Use optional chaining (`?.`) and nullish coalescing (`??`)
- Async/await over raw Promises
- Early returns to reduce nesting
