# Contributing to sorowatch-backend

## Setup
```
python -m venv .venv
.venv\Scripts\activate      # PowerShell
pip install -r requirements.txt
python -m pytest
uvicorn app.main:app --reload
```

## Before opening a PR
- Run python -m pytest and make sure it passes.
- Mock external calls (Soroban RPC, ai-agent) with respx in new tests —
  don't hit real network in the test suite.
- Keep the PR scoped to one issue; reference it with `Closes #N`.

## Related repos
- sorowatch-contract — the Soroban contract this service reads/writes
- sorowatch-ai-agent — the scoring service this backend calls
- sorowatch-frontend — dashboard consuming this service's endpoints
