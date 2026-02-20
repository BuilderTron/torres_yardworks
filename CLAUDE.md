# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Torres Yardworks is a Django website for a Houston landscaping/construction company. Multi-page marketing site with contact forms, gallery, service pages, and admin-managed content. Live at claude.

## Commands

Development uses Docker. All `inv` commands run inside the container:

```bash
inv up                 # Start dev containers (migrations run automatically)
inv down               # Stop containers
inv build              # Rebuild Docker image
inv logs               # Tail container logs
inv migrate            # Apply migrations
inv makemigrations     # Generate migrations
inv shell              # Django shell
inv test               # Run tests
inv createsuperuser    # Create admin user
inv bash               # Bash shell in container
inv manage '<cmd>'     # Run any manage.py command
```

## Dependencies

Managed with `uv` (not pip). Use `uv sync` to install, `uv add <pkg>` to add new dependencies. Dependencies defined in `pyproject.toml`, locked in `uv.lock`. Python 3.11 (pinned in `.python-version`).

## Architecture

**Two-package Django project:**

- `torres_web/` — Django project config (settings, root URLs, wsgi)
- `web_app/` — Single Django app containing all business logic

**Settings** (`torres_web/settings.py`): Uses `django-environ`. SQLite with WAL mode. Email backend configurable (console in dev, Gmail SMTP in prod). Static/media paths configurable via env vars.

**Dev env vars** are set in `compose.yaml` — no `.env` file needed for development.

**Models** (`web_app/models.py`):

- `HeroSlide`, `Event`, `Testimonies` — Admin-managed homepage content
- `GalleryCategorie`, `GalleryUpload` — Gallery with category FK relationship
- `ClientLeads` — Stores all form submissions (contact, quote, home quick form)

**Views** (`web_app/views.py`): All function-based views. Form-handling views (`home`, `contact`, `free_quote`) read `request.POST` directly (no Django Forms), save a `ClientLeads` instance, send email via `send_mail`, then render `thank_you.html`.

**Templates**: All in `web_app/templates/web_app/`, extending `base.html`. Static assets referenced via `{% static %}`, URLs via `{% url 'name' %}`.

**Admin** (`web_app/admin.py`): All models registered. `ClientLeads` uses `django-import-export` for CSV/Excel export.

**URL routing**: Root URLs in `torres_web/urls.py` include `web_app/urls.py`. All routes are flat (e.g., `/about`, `/gallery`, `/free_quote`). Admin at `/admin/`.
