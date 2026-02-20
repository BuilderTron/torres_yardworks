# Torres Yardworks

Marketing website for Torres Yardworks, a Houston landscaping and construction company.

Built with Django 5.1, served by Gunicorn behind Caddy (auto-SSL), deployed to DigitalOcean via GitHub Actions.

**Live:** [torresyardworks.com](https://torresyardworks.com)

## Quick Start

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- [uv](https://docs.astral.sh/uv/) + `uv sync` (for `inv` shortcuts)

### Development

```bash
inv up
```

Site: <http://localhost:8000> | Admin: <http://localhost:8000/admin/>

Migrations run automatically on start. Hot reload is enabled. Emails print to the container logs.

## Commands

All commands use [invoke](https://www.pyinvoke.org/) (`inv`) and run inside Docker:

| Command                | Description                      |
| ---------------------- | -------------------------------- |
| `inv up`               | Start dev containers             |
| `inv down`             | Stop dev containers              |
| `inv build`            | Rebuild Docker image             |
| `inv logs`             | Tail container logs              |
| `inv migrate`          | Run database migrations          |
| `inv makemigrations`   | Generate new migrations          |
| `inv shell`            | Open Django shell                |
| `inv test`             | Run tests                        |
| `inv createsuperuser`  | Create admin user                |
| `inv bash`             | Bash shell in container          |
| `inv manage '<cmd>'`   | Run any manage.py command        |

### Production

| Command          | Description                         |
| ---------------- | ----------------------------------- |
| `inv prod-logs`  | Tail production logs via SSH        |
| `inv prod-shell` | Django shell on production server   |
| `inv prod-backup`| Trigger manual backup on production |

Requires `DROPLET_IP` environment variable.

## Deployment

Push to `main` triggers automatic deployment via GitHub Actions:

1. Run tests
2. Build Docker image and push to GHCR
3. SSH into Droplet, pull image, restart services

See [docs/droplet-setup.md](docs/droplet-setup.md) for server provisioning.

## Architecture

```text
Internet → Caddy (ports 80/443, auto-SSL) → Gunicorn (port 8000) → SQLite
                    ↓
          /static/ and /media/ served directly
```

- **Web:** Django 5.1 + Gunicorn (2 workers, 2 threads)
- **Proxy:** Caddy 2 (TLS, static files, security headers, gzip)
- **Database:** SQLite with WAL mode
- **CI/CD:** GitHub Actions → GHCR → SSH deploy

## License

Copyright (c) Torres Yardworks
