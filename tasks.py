from invoke import task

COMPOSE = "docker compose"
EXEC = f"{COMPOSE} exec web"
MANAGE = f"{EXEC} python manage.py"


# --- Development (Docker) ---

@task
def up(c):
    """Start dev containers"""
    c.run(f"{COMPOSE} up", pty=True)

@task
def down(c):
    """Stop dev containers"""
    c.run(f"{COMPOSE} down")

@task
def build(c):
    """Rebuild Docker image"""
    c.run(f"{COMPOSE} build")

@task
def logs(c):
    """Tail dev container logs"""
    c.run(f"{COMPOSE} logs -f", pty=True)

@task
def migrate(c):
    """Run database migrations"""
    c.run(f"{MANAGE} migrate")

@task
def makemigrations(c):
    """Generate new migrations"""
    c.run(f"{MANAGE} makemigrations")

@task
def shell(c):
    """Open Django shell"""
    c.run(f"{MANAGE} shell", pty=True)

@task
def test(c):
    """Run tests"""
    c.run(f"{MANAGE} test")

@task
def createsuperuser(c):
    """Create admin user"""
    c.run(f"{MANAGE} createsuperuser", pty=True)

@task
def bash(c):
    """Open bash shell in container"""
    c.run(f"{EXEC} bash", pty=True)

@task
def manage(c, cmd):
    """Run any manage.py command. Usage: inv manage 'collectstatic --noinput'"""
    c.run(f"{MANAGE} {cmd}")


# --- Production (require DROPLET_IP env var) ---

@task
def prod_logs(c):
    """Tail production logs. Requires DROPLET_IP env var."""
    c.run(
        "ssh deploy@$DROPLET_IP "
        "'cd /opt/torres-yardworks && docker compose -f compose.prod.yaml logs -f'",
        pty=True,
    )

@task
def prod_shell(c):
    """Open Django shell on production. Requires DROPLET_IP env var."""
    c.run(
        "ssh -t deploy@$DROPLET_IP "
        "'cd /opt/torres-yardworks && docker compose -f compose.prod.yaml exec web python manage.py shell'",
        pty=True,
    )

@task
def prod_backup(c):
    """Trigger a backup on production. Requires DROPLET_IP env var."""
    c.run(
        "ssh deploy@$DROPLET_IP "
        "'cd /opt/torres-yardworks && bash scripts/backup.sh'",
        pty=True,
    )
