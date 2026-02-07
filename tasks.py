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
