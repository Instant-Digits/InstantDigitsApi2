# Setting Up `insdigits.today` with Vultr, Nginx, and SSL

## Step 1: Update DNS Settings

You need to point your domain (`insdigits.today`) to your Vultr server's IP address (`216.155.157.204`).

### Steps:

1. Log in to your **Dynadot** account.
2. Go to the **Domain Management** section.
3. Find your domain (`insdigits.today`) and click **Manage**.
4. Navigate to the **DNS Settings** or **Nameservers** section.
5. Add an **A record**:
   - **Host**: `@` (or leave it blank for the root domain)
   - **Value**: `216.155.157.204` (your Vultr server's IP)
   - **TTL**: Leave as default (e.g., 3600 seconds)
6. Save the changes.

### Optional: Add a Subdomain

If you want to use a subdomain (e.g., `api.insdigits.today`), add another **A record**:

- **Host**: `api`
- **Value**: `216.155.157.204`
- **TTL**: Leave as default.

---

## Step 2: Set Up Nginx as a Reverse Proxy

Nginx will act as a reverse proxy to route traffic from `insdigits.today` to your Flask app running on port 5000.

### Steps:

#### Install Nginx:

```bash
sudo apt update
sudo apt install nginx
```

#### Configure Nginx:

Create a new configuration file for your domain:

```bash
sudo nano /etc/nginx/sites-available/insdigits.today
```

Add the following configuration:

```nginx
server {
    listen 80;
    server_name insdigits.today;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Save and exit (Ctrl + O, then Ctrl + X).

#### Enable the Configuration:

```bash
sudo ln -s /etc/nginx/sites-available/insdigits.today /etc/nginx/sites-enabled/
```

#### Test and Restart Nginx:

```bash
sudo nginx -t
sudo systemctl restart nginx
```

---

## Step 3: Check Firewall Settings

Ensure that ports 80 (HTTP) and 443 (HTTPS) are open:

```bash
sudo ufw status
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw reload
```

---

## Step 4: Set Up HTTPS with Let's Encrypt

To secure your domain with HTTPS, use Let's Encrypt.

### Steps:

#### Install Certbot:

```bash
sudo apt install certbot python3-certbot-nginx
```

#### Obtain an SSL Certificate:

```bash
sudo certbot --nginx -d insdigits.today
```

Run a dry-run to test certificate renewal:

```bash
sudo certbot renew --dry-run
```

Check the status of Nginx:

```bash
sudo systemctl status nginx
```

Restart Nginx:

```bash
sudo systemctl restart nginx
```

Follow the prompts to complete the process.

#### Verify HTTPS:

Visit `https://insdigits.today` in your browser.

---

## Step 5: Update Flask App Configuration

Ensure your Flask app is running on `127.0.0.1:5000` so that Nginx can forward requests to it.

### Example Flask App:

```python
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "Hello, World!"

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)
```

### Run your Flask app:

```bash
python app.py
```

Test with `curl`:

```bash
curl http://127.0.0.1:5000
```

---

## Step 6: Test the Setup

Visit `https://insdigits.today` in your browser. You should see the response from your Flask app (e.g., "Hello, World!").

---

## Step 7: Optional - Set Up a Subdomain

If you want to use a subdomain (e.g., `api.insdigits.today`), follow these steps:

### Add a DNS A Record:

In **Dynadot**, add an A record for the subdomain:

- **Host**: `api`
- **Value**: `216.155.157.204`
- **TTL**: Default.

### Update Nginx Configuration:

Edit your Nginx configuration file:

```bash
sudo nano /etc/nginx/sites-available/insdigits.today
```

Add a new server block for the subdomain:

```nginx
server {
    listen 80;
    server_name api.insdigits.today;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Save and exit the file.

#### Obtain an SSL Certificate for the Subdomain:

```bash
sudo certbot --nginx -d api.insdigits.today
```

#### Restart Nginx:

```bash
sudo systemctl restart nginx
```

#### Test the Subdomain:

Visit `https://api.insdigits.today` in your browser.
