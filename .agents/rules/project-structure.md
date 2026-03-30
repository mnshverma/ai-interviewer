# Project Structure — AI Interviewer

## Standard Structure

```
ai-interviewer/
├── .agents/                    ← AI agent configuration
│   ├── CONTEXT.md              ← Project context (architecture, file map)
│   ├── CONTEXT.local.md        ← Local state, progress, TODO
│   ├── workflows/              ← Agent workflow commands
│   ├── rules/                  ← Mandatory AI rules
│   └── skills/                 ← Specialized skills
├── src/                        ← ALL source code
│   ├── App.jsx                 ← Main orchestrator (state + flow)
│   ├── main.jsx                ← React entry (DO NOT modify)
│   ├── index.css               ← Single CSS file (design system)
│   ├── components/             ← React components (one per file)
│   │   └── *.jsx
│   ├── utils/                  ← Pure utility modules (no React)
│   │   └── *.js
│   └── assets/                 ← Static imports (images, icons)
├── public/                     ← Unprocessed static assets
├── dist/                       ← Build output (git-ignored)
├── .env                        ← Secrets (git-ignored)
├── .env.example                ← Env template (committed)
├── package.json
├── vite.config.js
├── vercel.json
├── eslint.config.js
└── README.md
```

## Rules for Adding Files

### New Component
1. Create `src/components/MyComponent.jsx`
2. Use PascalCase filename matching the component name
3. Export as `default`
4. Import and use in `App.jsx` or parent component
5. Add styles to `src/index.css` (never create per-component CSS files)

### New Utility
1. Create `src/utils/myUtility.js`
2. Use camelCase filename
3. Export named functions (not default)
4. Keep React-free — pure JavaScript logic only
5. Utility should be importable by any component

### New Page/View
This app is a single-page app (SPA). There are no routes or pages.
Different "views" are controlled by the `interviewState` state machine in `App.jsx`.
To add a new view:
1. Add a new state value in `App.jsx`
2. Add conditional rendering in `App.jsx`'s return JSX
3. Create the component in `src/components/`

## Files That Should NOT Be Modified
- `src/main.jsx` — React entry point, no logic belongs here
- `vite.config.js` — Only modify when adding Vite plugins
- `eslint.config.js` — Only modify when adding lint rules

## Files That Should NOT Be Created
- No `src/styles/` directory — all CSS lives in `src/index.css`
- No `src/context/` — no React Context is used
- No `src/hooks/` — keep hooks in the component that uses them
- No `src/pages/` — this is not a multi-page app
- No `src/services/` — use `src/utils/` instead
