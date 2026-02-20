# DigitalOcean Droplet Setup Guide

Step-by-step guide to provision a Droplet and deploy Torres Yardworks.

## 1. Create the Droplet

In the DigitalOcean dashboard:

- **Image:** Ubuntu 24.04 LTS
- **Plan:** Basic, s-1vcpu-2gb ($12/mo)
- **Region:** Choose the closest to Houston (e.g., SFO3 or NYC3)
- **Authentication:** SSH key (add your public key)
- **Hostname:** `torres-yardworks`

Note the Droplet IP address after creation.

## 2. Initial Server Setup (as root)

SSH into the Droplet:

```bash
ssh root@YOUR_DROPLET_IP
```

### Create the `deploy` user

```bash
adduser --disabled-password --gecos "" deploy
mkdir -p /home/deploy/.ssh
cp /root/.ssh/authorized_keys /home/deploy/.ssh/authorized_keys
chown -R deploy:deploy /home/deploy/.ssh
chmod 700 /home/deploy/.ssh
chmod 600 /home/deploy/.ssh/authorized_keys
```

### Configure firewall

```bash
ufw allow OpenSSH
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 443/udp   # HTTP/3 (QUIC)
ufw --force enable
ufw status
```

### Install Docker (official Docker apt repo)

```bash
# Install prerequisites
apt-get update
apt-get install -y ca-certificates curl

# Add Docker's official GPG key
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
chmod a+r /etc/apt/keyrings/docker.asc

# Add the Docker apt repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker
apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Add deploy user to docker group
usermod -aG docker deploy
```

### Disable root SSH login

```bash
sed -i 's/^PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
sed -i 's/^#PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config
systemctl restart sshd
```

> After this step, log out and re-login as `deploy` user to verify access
> before closing your root session.

### Set up the project directory

```bash
mkdir -p /opt/torres-yardworks/backups
chown -R deploy:deploy /opt/torres-yardworks
```

## 3. First Deploy

SSH in as the `deploy` user:

```bash
ssh deploy@YOUR_DROPLET_IP
```

### Copy configuration files to the Droplet

From your **local machine**, copy the required files:

```bash
scp compose.prod.yaml deploy@YOUR_DROPLET_IP:/opt/torres-yardworks/
scp Caddyfile deploy@YOUR_DROPLET_IP:/opt/torres-yardworks/
scp scripts/backup.sh deploy@YOUR_DROPLET_IP:/opt/torres-yardworks/scripts/
```

### Create the production environment file

On the Droplet:

```bash
cd /opt/torres-yardworks
nano .env.prod
```

Add your production values (see `.env.prod.example` in the repo for reference):

```
SECRET_KEY=your-long-random-secret-key
DEBUG=False
ALLOWED_HOSTS=torresyardworks.com,www.torresyardworks.com
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

Generate a secret key:

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(50))"
```

### Pull and start the containers

```bash
cd /opt/torres-yardworks

# Log in to GitHub Container Registry (use a personal access token with read:packages scope)
echo "YOUR_GITHUB_PAT" | docker login ghcr.io -u YOUR_GITHUB_USERNAME --password-stdin

# Pull the latest image and start services
docker compose -f compose.prod.yaml pull
docker compose -f compose.prod.yaml up -d

# Check that services are healthy
docker compose -f compose.prod.yaml ps
```

### Create the Django superuser

```bash
docker compose -f compose.prod.yaml exec web python manage.py createsuperuser
```

### Point DNS to the Droplet

In your domain registrar (Porkbun, Cloudflare, etc.), set:

- `A` record: `torresyardworks.com` -> `YOUR_DROPLET_IP`
- `A` record: `www.torresyardworks.com` -> `YOUR_DROPLET_IP`

Caddy will automatically obtain and renew TLS certificates once DNS propagates.

## 4. Set Up Automated Backups

Copy the backup script and make it executable:

```bash
mkdir -p /opt/torres-yardworks/scripts
# (Already copied via scp above)
chmod +x /opt/torres-yardworks/scripts/backup.sh
```

Add a cron job for daily backups at 3:00 AM:

```bash
crontab -e
```

Add this line:

```
0 3 * * * /opt/torres-yardworks/scripts/backup.sh >> /var/log/torres-backup.log 2>&1
```

Test the backup manually:

```bash
/opt/torres-yardworks/scripts/backup.sh
ls -la /opt/torres-yardworks/backups/
```

## 5. GitHub Actions Setup

For automated deployments, add these secrets to your GitHub repository
(Settings > Secrets and variables > Actions):

| Secret            | Value                                                 |
| ----------------- | ----------------------------------------------------- |
| `DROPLET_IP`      | Your Droplet's IP address                             |
| `SSH_PRIVATE_KEY`  | SSH private key for the `deploy` user                |

### Generate a deploy-only SSH key pair

On your local machine:

```bash
ssh-keygen -t ed25519 -C "github-actions-deploy" -f ~/.ssh/torres_deploy -N ""
```

Copy the public key to the Droplet:

```bash
ssh-copy-id -i ~/.ssh/torres_deploy.pub deploy@YOUR_DROPLET_IP
```

Copy the **private key** contents and add it as the `SSH_PRIVATE_KEY` GitHub secret:

```bash
cat ~/.ssh/torres_deploy
```

## 6. Verify Deployment

After the first deploy:

1. Visit `https://torresyardworks.com` -- should show the site with a valid TLS certificate
2. Visit `https://torresyardworks.com/admin/` -- log in with your superuser credentials
3. Visit `https://torresyardworks.com/health/` -- should return `{"status": "ok"}`
4. Check container health: `docker compose -f compose.prod.yaml ps`
5. Check logs: `docker compose -f compose.prod.yaml logs -f`

## Troubleshooting

### Containers not starting

```bash
docker compose -f compose.prod.yaml logs web
docker compose -f compose.prod.yaml logs caddy
```

### Caddy not getting TLS certificate

- Ensure DNS A records point to the Droplet IP
- Ensure ports 80 and 443 are open (`ufw status`)
- Check Caddy logs: `docker compose -f compose.prod.yaml logs caddy`

### Database issues

```bash
# Run migrations manually
docker compose -f compose.prod.yaml exec web python manage.py migrate

# Open Django shell
docker compose -f compose.prod.yaml exec web python manage.py shell
```

### Disk space

```bash
# Check disk usage
df -h

# Clean up old Docker images
docker image prune -a -f
docker system prune -f
```
