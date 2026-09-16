## Plan: Add AAA FastAPI Tests

Add a dedicated `tests/test_api.py` suite for the FastAPI endpoints using explicit Arrange-Act-Assert sections. Preserve the existing `tests/test_app.py` test.

**Steps**
1. Create `tests/test_api.py` using the existing `TestClient` setup.
2. Add AAA tests for:
   - Root redirect
   - Activity listing
   - Successful signup and unregister
   - Unknown activities
   - Duplicate signup
   - Full activity
   - Unregistering a nonparticipant
3. Use unique emails and restore shared activity state where needed to prevent test-order dependence.
4. Run:
   - `pytest tests/test_api.py tests/test_app.py`
   - `pytest`

**Relevant files**
- [tests/test_api.py](tests/test_api.py) — new backend API test module.
- [tests/test_app.py](tests/test_app.py) — existing test and import pattern.
- [src/app.py](src/app.py) — API behavior under test.

**Decisions**
- Add `tests/test_api.py` rather than reorganizing the existing test.
- Test public HTTP responses, JSON payloads, redirects, and participant state.
- No production-code changes are planned.
