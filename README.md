# Torres Contractors Website 2021
**Version 2**

This is Torres Yardworks website managed by
Jose J. Lopez.

---

## Contents

- About
- Services
- Galleries
- Contact
---

## License & copyright

Copyright (c) [2021] [Torres Yardworks]

---

## Link
[torresyardworks.com]()

---

## Development Setup

### Prerequisites
- [uv](https://github.com/astral-sh/uv) (for dependency management)
- Docker (optional, for containerized environment)

### Local Development
1.  **Install dependencies**:
    ```bash
    uv sync
    ```

2.  **Activate virtual environment**:
    ```bash
    source .venv/bin/activate
    ```

3.  **Start the server**:
    ```bash
    inv dev
    ```

The site will be available at **[http://localhost:8000](http://localhost:8000)**.
Access the admin panel at **[http://localhost:8000/admin](http://localhost:8000/admin)**.

### Docker
To run using Docker:

1.  **Activate virtual environment** (if not already active):
    ```bash
    source .venv/bin/activate
    ```

2.  **Start the container**:
    ```bash
    inv docker-up
    ```
    (Or `docker compose up`)

The site will be available at same address: **[http://localhost:8000](http://localhost:8000)**.
**Auto-reload enabled**: Changes to your code will automatically reload the server in the container.

### Common Commands (in Docker)
To run commands *inside* the running container:

- `inv docker-run migrate` - Run migrations inside Docker
- `inv docker-run makemigrations` - Make migrations inside Docker
- `inv docker-shell` - Open a bash shell inside the container

### Common Commands (Local)
- `inv migrate` - Run database migrations locally
- `inv makemigrations` - Create new migrations locally
