---
description: How to review code changes in the AI Interviewer project
---

# Review Workflow (Python)

Follow these steps to perform a code review on the Python-native AI Interviewer.

## Prerequisites

- [ ] Python 3.9+
- [ ] streamlit installed (`pip install streamlit`)
- [ ] PyPDF2 and requests installed

## Step 1: Quality Check

1. Check Python syntax and style (if available):
   ```bash
   flake8 app.py
   ```
2. Verify all `import` statements are correct and in alphabetical order.
3. Check for any commented-out code that should be removed.
4. Ensure all global constant values (`KILO_API_URL`, `DEFAULT_MODEL`) are at the top of the file.

## Step 2: Logic Audit

Check the core AI functions:
- [ ] `call_ai`: Ensure it handles non-200 responses and timeouts correctly.
- [ ] `extract_text_from_pdf`: Ensure it iterates through all pages and handles errors.
- [ ] `session_state`: Verify it's correctly used to manage step-based routing.
- [ ] `prompt_engineering`: Review the system and user messages for clarity and role-playing.

## Step 3: Security Review

1. Key exposure check:
   ```bash
   grep "ki-" app.py
   ```
2. User input check:
   - [ ] No `eval()` or `exec()` usage.
   - [ ] Prompt construction uses f-strings with contextually sanitized variables.
   - [ ] File uploads only accept `.pdf`.

## Step 4: UI/UX Flow

Run the app locally to test the flow:
```bash
streamlit run app.py
```
- [ ] **Home**: Resume upload is functional.
- [ ] **Analysis**: Text extraction is accurate and summary is displayed.
- [ ] **Questions**: 8 questions are generated from the analysis.
- [ ] **Interview**: User can provide answers and move to the next question.
- [ ] **Report**: Final summary is generated based on the session transcript.

## Final Approval

Once all steps are verified:
1. Merge the PR or finalize the commit.
2. Tag the version (e.g., `v2.0.0-python`).
3. Deploy to production using the `/deploy` workflow.
