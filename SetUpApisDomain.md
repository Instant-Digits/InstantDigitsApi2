# Setting Up `apis.instantdigits.com` and `files.instantdigits.com` with Vultr, Nginx, and SSL

---

## Step 1: Update DNS Settings

Log in to your DNS provider (e.g., Dynadot) and create A records pointing to your server IP (`216.155.157.204`):

| Subdomain               | Type | Value (Your Server IP) |
| ----------------------- | ---- | ---------------------- |
| apis.instantdigits.com  | A    | 216.155.157.204        |
| files.instantdigits.com | A    | 216.155.157.204        |

---

## Step 2: Set Up Nginx for `apis.instantdigits.com`

This will reverse proxy requests to your FastAPI app running on port 5000.

### Create Nginx Configuration:

```bash
sudo nano /etc/nginx/sites-available/apis.instantdigits.com
```

Paste:

```nginx
server {
    listen 80;
    server_name apis.instantdigits.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        proxy_buffering off;
        proxy_cache off;
        chunked_transfer_encoding on;

        proxy_connect_timeout 60s;
        proxy_send_timeout 600s;
        proxy_read_timeout 600s;
        send_timeout 600s;
    }
}
```

Enable the configuration:

```bash
sudo ln -s /etc/nginx/sites-available/apis.instantdigits.com /etc/nginx/sites-enabled/
```

---

## Step 3: Set Up Nginx for `files.instantdigits.com`

This will serve static files located at `/home/ubuntu/InstantDigitsApi2/public`.

### Create symbolic link for Nginx:

```bash
sudo rm -rf /var/www/files
sudo ln -s /home/ubuntu/InstantDigitsApi2/public /var/www/files
```

### Create Nginx Configuration:

```bash
sudo nano /etc/nginx/sites-available/files.instantdigits.com
```

Paste:

```nginx
server {
    listen 80;
    server_name files.instantdigits.com;

    root /var/www/files;
    index index.html;

    location / {
        try_files $uri $uri/ =404;
    }
}
```

Enable the configuration:

```bash
sudo ln -s /etc/nginx/sites-available/files.instantdigits.com /etc/nginx/sites-enabled/
```

---

## Step 4: Test and Reload Nginx

```bash
sudo nginx -t
sudo systemctl reload nginx
```

---

## Step 5: Install SSL Certificates with Certbot

Make sure Certbot is installed:

```bash
sudo apt install certbot python3-certbot-nginx
```

Obtain and configure SSL certificates:

```bash
sudo certbot --nginx -d apis.instantdigits.com
sudo certbot --nginx -d files.instantdigits.com
```

---

## Step 6: Verify Setup

- Visit `https://apis.instantdigits.com` → FastAPI app should respond.
- Visit `https://files.instantdigits.com/yourfile.ext` → Static file should be served.

---

## Step 7: Test Auto-Renewal of SSL Certificates

```bash
sudo certbot renew --dry-run
```

---

## Step 8: Firewall Settings (if applicable)

Ensure HTTP and HTTPS ports are open:

```bash
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw reload
```

---

_End of Document_
