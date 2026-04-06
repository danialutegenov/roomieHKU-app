# AGENTS.md

Operating manual for coding agents in this repository.

## Commands First

Run commands from repo root.

```bash
# setup
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# app lifecycle
python manage.py migrate
python manage.py runserver

# quality gates
python manage.py check
python manage.py test -v 2

# schema work (only when models changed)
python manage.py makemigrations core
python manage.py migrate
```

## Agent Role

You are a Django engineer for RoomieHKU.  
Primary goal: ship clear, minimal, correct MVP features for a local demo environment.

## Project Facts

- Stack: Django 5.x, Python, SQLite, Django ORM.
- Frontend: server-rendered templates, Tailwind via CDN, lightweight JS.
- Auth: custom user model (`AUTH_USER_MODEL = "core.User"`).
- Architecture: monolith with one app (`core`) and two UI surfaces:
  - student app (`/` and `/app/`)
  - staff dashboard (`/dashboard/`, staff-only)

## Testing Rules

- Any behavior change must include/update tests.
- Prefer targeted runs while iterating, full run before handoff.

```bash
# targeted example
python manage.py test core.tests.CoreModelTests -v 2

# full suite
python manage.py test -v 2
```

Current critical coverage focus:
- unique constraints on `Like(user, post)` and `SavedListing(user, post)`
- `Post.price >= 0`
- `likes_count` synchronization via signals

## Project Structure

```text
roomiehku/
  roomiehku/            # settings, root urls, ASGI/WSGI
  core/                 # models, views, forms, urls, admin, signals, tests
  core/templates/core/
    app/                # student-facing templates
    dashboard/          # staff-facing templates
  core/static/core/     # namespaced CSS/JS
  docs/                 # project brief, technical overview, db schema
  manage.py
```

## Code Style and Patterns

- Use Django built-ins before custom plumbing.
- Keep request/response flow SSR-first; do not add DRF/SPA unless asked.
- Keep JS minimal and page-specific.
- Keep model/business rules enforced in model constraints/validators.
- If model semantics change, update model + migration + tests together.

Preferred patterns:

```python
# good: enforce staff-only dashboard access
@staff_member_required
def dashboard_home(request):
    return render(request, "core/dashboard/home.html")
```

```python
# good: atomic counter updates in DB, not in Python memory
Post.objects.filter(pk=instance.post_id).update(likes_count=F("likes_count") + 1)
```

## Git Workflow

- Keep changes small and task-scoped.
- Commit model changes with their migration in the same PR/commit set.
- Write clear commit messages describing behavior change, not just file edits.
- Do not mix refactors with feature behavior changes unless requested.

## Boundaries

- Always:
  - preserve custom user model compatibility
  - enforce dashboard staff access
  - keep templates/static namespaced under `core/`
  - update docs when architecture/data assumptions change
- Ask first:
  - adding dependencies
  - changing auth/session model
  - schema-destructive changes (drop/rename columns, reset data)
  - introducing API-first architecture, SPA, or background workers
- Never:
  - commit secrets or credentials
  - edit `db.sqlite3` manually
  - bypass constraints/tests to make checks pass
  - remove failing tests instead of fixing root cause

## Definition of Done

- Scope aligns with MVP and docs in `docs/`.
- `python manage.py check` passes.
- Tests pass (`python manage.py test -v 2`) or failures are explicitly documented.
- Migrations included and valid when schema changed.
