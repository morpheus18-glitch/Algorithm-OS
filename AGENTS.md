# Repository Guidelines

These instructions apply to the entire repository. Follow them when updating or creating files.

## Required Checks

Before committing, run:

```bash
python -m py_compile backend/main.py backend/algorithms/*.py
```

This ensures all backend modules compile correctly. Fix any syntax errors before continuing.

Verify the frontend structure exists:

- `frontend/css`
- `frontend/js`
- `frontend/libs`
- `frontend/sample_data`

If any directory is missing, create it or update references so the dashboard works out of the box.

## Code Quality

Keep the code cohesive. When modifying one file, update related files so the application remains functional. Avoid placeholders; include production-ready code.

Use `./start.sh` to manually test that backend and frontend launch together.
