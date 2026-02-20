from invoke import task

@task
def dev(c):
    """Run development server"""
    c.run("python manage.py runserver 0.0.0.0:8000")

@task
def migrate(c):
    """Run migrations"""
    c.run("python manage.py migrate")

@task
def makemigrations(c):
    """Make migrations"""
    c.run("python manage.py makemigrations")

@task
def shell(c):
    """Run shell"""
    c.run("python manage.py shell")

@task
def test(c):
    """Run tests"""
    c.run("python manage.py test")

@task
def docker_build(c):
    """Build Docker image"""
    c.run("docker compose build")

@task
def docker_up(c):
    """Start Docker services"""
    c.run("docker compose up")

@task
def docker_down(c):
    """Stop Docker services"""
    c.run("docker compose down")

@task
def docker_run(c, cmd):
    """Run a command inside the docker container. Usage: inv docker-run 'migrate'"""
    c.run(f"docker compose exec web inv {cmd}")

@task
def docker_shell(c):
    """Open a shell inside the docker container"""
    c.run("docker compose exec web bash")


# --- Production tasks (require DROPLET_IP env var) ---

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
