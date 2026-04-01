# Testing — AI Interviewer

## Current Testing Approach
This project uses **manual testing** as the primary QA method. No automated test framework is currently configured.

## Manual Testing Checklist

### Device Testing (device_test)
- [ ] Camera permission prompt appears
- [ ] Microphone permission prompt appears
- [ ] Live camera preview works
- [ ] Microphone level visualizer works
- [ ] "Done - Continue to Photo" works

### Photo Capture (photo_capture)
- [ ] Camera feed displays
- [ ] Photo capture works
- [ ] Preview shows after capture
- [ ] "Continue →" proceeds to setup

### Setup/Candidate Details (setup)
- [ ] All form fields accept input
- [ ] Resume PDF upload works
- [ ] JD text area accepts input
- [ ] Model dropdown shows available models
- [ ] Form validation shows errors for empty fields
- [ ] "Start Interview Session" proceeds to analysis

### Analysis (analysis)
- [ ] AI analysis displays correctly
- [ ] Candidate info shows correctly
- [ ] "Confirm & Proceed to Interview" works

### Interview (interview)
- [ ] Questions display correctly
- [ ] Answer text area works
- [ ] Voice input button works
- [ ] Navigation (Next/Previous) works
- [ ] Progress bar updates
- [ ] Proctoring camera works

### Report (report)
- [ ] AI evaluation displays
- [ ] PASS/FAIL badge shows correctly
- [ ] Transcript view works
- [ ] "Start New Interview" resets everything

### Cross-Browser
- [ ] Chrome (primary)
- [ ] Edge
- [ ] Firefox

### Responsive
- [ ] Desktop (1920px+)
- [ ] Laptop (1366px)
- [ ] Tablet (768px)
- [ ] Mobile (375px)

## Python Syntax Check

Before every commit, verify syntax:
```bash
python -m py_compile app.py
```

Or:
```bash
python -c "import ast; ast.parse(open('app.py').read())"
```

## Linting (Optional)

Install and run black for formatting:
```bash
pip install black
black app.py --line-length 100
```

## Future: Automated Testing

### Planned Stack
```
pip install pytest pytest-cov
```

### Test Targets
- API calls (`call_ai` function)
- PDF parsing (`extract_text_from_pdf`)
- PDF report generation (`create_pdf_report`)
- State transitions

### Test Convention
```
tests/
├── test_api.py
├── test_parsing.py
└── test_report.py
```