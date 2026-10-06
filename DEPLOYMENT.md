# 🚀 Free Deployment Guide for Placement Management System

This guide covers multiple **free** deployment options for your Django Placement Management System.

---

## 📋 Prerequisites

Before deploying, ensure you have:
- ✅ GitHub account
- ✅ Project pushed to a GitHub repository
- ✅ `requirements.txt` updated (run `pip freeze > requirements.txt`)
- ✅ `render.yaml` already exists (for Render deployment)

---

## 🎯 Option 1: Render (Recommended) — ⭐ Easiest for Django

> 🌐 **Live App URL:** [https://placement-system-bpbb.onrender.com/](https://placement-system-bpbb.onrender.com/)

**Free Tier**: 750 hours/month, PostgreSQL database, SSL, custom domains

### Step 1: Push to GitHub
```bash
git init
git add .
git commit -m "Initial commit for deployment"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/placement_system.git
git push -u origin main
```

### Step 2: Deploy on Render
1. Go to [render.com](https://render.com) → Sign up with GitHub
2. Click **"New +"** → **"Blueprint"**
3. Connect your repository
4. Render will detect `render.yaml` and auto-configure:
   - Web Service (Python/Django)
   - PostgreSQL Database
   - Environment variables (SECRET_KEY, DATABASE_URL)
5. Click **"Apply"** — deployment starts automatically!

### Step 3: Post-Deploy Setup
```bash
# In Render Shell (or locally with production settings)
python manage.py createsuperuser
```

### Render Free Tier Limits
| Resource | Limit |
|----------|-------|
| Web Service | 750 hrs/month (spins down after 15 min inactivity) |
| PostgreSQL | 90 days free, then $7/mo (or migrate to Supabase/Neon) |
| Bandwidth | 100 GB/month |
| Static Files | Served via WhiteNoise (included) |

---

## 🎯 Option 2: Railway — ⭐ Best Free PostgreSQL

**Free Tier**: $5 credit/month (enough for small Django + PostgreSQL)

### Deploy Steps
1. Go to [railway.app](https://railway.app) → Sign up with GitHub
2. **"New Project"** → **"Deploy from GitHub repo"**
3. Select your repo
4. Add **PostgreSQL** database: **"New"** → **"Database"** → **"PostgreSQL"**
5. Railway auto-detects Django, but add these variables:
   ```
   SECRET_KEY=your-generated-secret-key
   DEBUG=False
   ALLOWED_HOSTS=your-app.up.railway.app
   DATABASE_URL=postgresql://... (auto-filled from Railway PostgreSQL)
   ```
6. **Deploy** — done!

### Railway Advantages
- ✅ Persistent PostgreSQL (no 90-day limit like Render)
- ✅ $5/month credit covers small apps indefinitely
- ✅ Automatic HTTPS, custom domains
- ✅ Easy CLI: `railway login && railway up`

---

## 🎯 Option 3: Fly.io — ⭐ Best for Global Performance

**Free Tier**: 3 shared-cpu-1x VMs, 160GB bandwidth, 3GB persistent volume

### Deploy Steps
```bash
# 1. Install Fly CLI
curl -L https://fly.io/install.sh | sh

# 2. Login & launch
fly auth login
fly launch --name placement-system --region ord

# 3. Create PostgreSQL (free tier)
fly postgres create --name placement-db --region ord --initial-cluster-size 1

# 4. Attach database
fly postgres attach placement-db

# 5. Set secrets
fly secrets set SECRET_KEY="$(openssl rand -base64 32)"
fly secrets set DEBUG=False
fly secrets set ALLOWED_HOSTS="placement-system.fly.dev"

# 6. Deploy
fly deploy
```

### Fly.io Advantages
- ✅ Global edge deployment (fast worldwide)
- ✅ Persistent volumes for media files
- ✅ Generous free allowance
- ✅ Native IPv6, private networking

---

## 🎯 Option 4: PythonAnywhere — ⭐ Beginner-Friendly

**Free Tier**: 1 web app at `yourusername.pythonanywhere.com`, 512MB disk, 1 MySQL/PostgreSQL DB

### Deploy Steps
1. Sign up at [pythonanywhere.com](https://pythonanywhere.com)
2. **Web** tab → **"Add a new web app"** → **Manual configuration** → **Python 3.11**
3. **Bash console**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/placement_system.git
   cd placement_system
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
4. **Web tab** → Set:
   - **Source code**: `/home/yourusername/placement_system`
   - **Working directory**: `/home/yourusername/placement_system`
   - **WSGI file**: Edit to match below
5. **WSGI Configuration** (`/var/www/yourusername_pythonanywhere_com_wsgi.py`):
   ```python
   import os, sys
   path = '/home/yourusername/placement_system'
   if path not in sys.path:
       sys.path.insert(0, path)
   os.environ['DJANGO_SETTINGS_MODULE'] = 'placement_system.settings'
   from django.core.wsgi import get_wsgi_application
   application = get_wsgi_application()
   ```
6. **Static files** mapping:
   - URL: `/static/` → Directory: `/home/yourusername/placement_system/staticfiles`
   - URL: `/media/` → Directory: `/home/yourusername/placement_system/media`
7. Run migrations & collectstatic in Bash console:
   ```bash
   python manage.py migrate
   python manage.py collectstatic --noinput
   python manage.py createsuperuser
   ```
8. **Reload** web app

---

## 🎯 Option 5: Koyeb — ⭐ Free Tier with Global Edge

**Free Tier**: 1 nano service (512MB RAM), 1GB bandwidth, global edge

### Deploy Steps
1. Go to [koyeb.com](https://koyeb.com) → Sign up with GitHub
2. **"Create App"** → **GitHub** → Select repo
3. **Builder**: Dockerfile (create one below) or Buildpack
4. **Environment variables**:
   ```
   SECRET_KEY=your-secret
   DEBUG=False
   ALLOWED_HOSTS=your-app.koyeb.app
   DATABASE_URL=postgresql://... (add Koyeb Postgres addon)
   ```
5. **Deploy**

### Dockerfile for Koyeb (create `Dockerfile` in root):
```dockerfile
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "placement_system.wsgi:application", "--bind", "0.0.0.0:8000"]
```

---

## 🗄️ Free PostgreSQL Alternatives (if not using Render/Railway/Fly)

| Service | Free Tier | Best For |
|---------|-----------|----------|
| **Neon** | 3GB storage, autoscaling | Serverless, branching |
| **Supabase** | 500MB PostgreSQL + Auth + Realtime | Full backend-as-a-service |
| **ElephantSQL** | 20MB (Tiny) | Very small apps only |
| **Aiven** | 1GB (trial) | Short-term projects |

### Using Neon (Recommended Free PostgreSQL)
1. Sign up at [neon.tech](https://neon.tech)
2. Create project → Copy connection string
3. Add to your hosting platform as `DATABASE_URL`
4. Run migrations: `python manage.py migrate`

---

## 📁 Media Files Handling (Resumes, Logos, Documents)

**Critical**: Free tiers have ephemeral filesystems. Choose ONE:

### Option A: Cloudinary (Free: 25GB storage, 25GB bandwidth)
1. Sign up at [cloudinary.com](https://cloudinary.com)
2. Add to `requirements.txt`:
   ```
   django-cloudinary-storage==0.3.0
   cloudinary==1.44.1
   ```
3. Update `settings.py`:
   ```python
   # Add to INSTALLED_APPS (before 'core')
   'cloudinary_storage',
   'cloudinary',
   
   # Media storage
   DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
   
   # Cloudinary config
   CLOUDINARY_STORAGE = {
       'CLOUD_NAME': config('CLOUDINARY_CLOUD_NAME'),
       'API_KEY': config('CLOUDINARY_API_KEY'),
       'API_SECRET': config('CLOUDINARY_API_SECRET'),
   }
   ```
4. Add Cloudinary credentials to hosting platform env vars

### Option B: AWS S3 / Cloudflare R2 (Free tier available)
- Similar setup with `django-storages`

### Option C: Keep Local (Only for Fly.io/Railway with volumes)
- Fly.io: `fly volumes create media --size 1`
- Railway: Add volume in service settings

---

## 🔧 Production Settings Checklist

Update `placement_system/settings.py` for production:

```python
# 1. Security (already in your settings.py - good!)
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

# 2. Allowed hosts (set via env var)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=Csv(), default='localhost,127.0.0.1')

# 3. Static files (WhiteNoise already configured)
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# 4. Database (uses dj_database_url - already configured)
DATABASES = {
    'default': config('DATABASE_URL', default=..., cast=dj_database_url.parse)
}

# 5. Email (configure for production)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')  # App password!

# 6. Logging (add to settings.py)
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {'class': 'logging.StreamHandler'},
    },
    'root': {'handlers': ['console'], 'level': 'INFO'},
}
```

---

## 🌐 Custom Domain (Free)

### Cloudflare (Free DNS + SSL + CDN)
1. Add domain to [Cloudflare](https://cloudflare.com)
2. Update nameservers at registrar
3. Add CNAME: `www` → `your-app.render.com` (or Railway/Fly URL)
4. Enable **"Orange Cloud"** (proxy) for free SSL + DDoS protection
5. Add domain in hosting platform settings

---

## 🔐 Environment Variables Checklist

| Variable | Required | Example |
|----------|----------|---------|
| `SECRET_KEY` | ✅ | `openssl rand -base64 32` |
| `DEBUG` | ✅ | `False` |
| `ALLOWED_HOSTS` | ✅ | `your-app.render.com,yourdomain.com` |
| `DATABASE_URL` | ✅ | `postgresql://user:pass@host:5432/db` |
| `EMAIL_HOST_USER` | For emails | `your@gmail.com` |
| `EMAIL_HOST_PASSWORD` | For emails | `app-password` |
| `CLOUDINARY_*` | For media | (if using Cloudinary) |

---

## 📊 Monitoring & Maintenance (Free)

| Tool | Purpose | Free Tier |
|------|---------|-----------|
| **UptimeRobot** | Uptime monitoring | 50 monitors, 5-min checks |
| **Sentry** | Error tracking | 5K errors/month |
| **Logtail** | Log management | 1GB/month |
| **Healthchecks.io** | Cron monitoring | 20 checks |

---

## 🎯 Quick Comparison: Which to Choose?

| Need | Best Option |
|------|-------------|
| **Easiest Django deploy** | **Render** (Blueprint + auto PostgreSQL) |
| **Persistent free PostgreSQL** | **Railway** ($5 credit/month) |
| **Global performance** | **Fly.io** (edge network) |
| **Beginner / no CLI** | **PythonAnywhere** (web UI) |
| **Docker / custom build** | **Koyeb** / **Fly.io** |
| **Serverless PostgreSQL** | **Neon** / **Supabase** (pair with any) |

---

## 🚀 My Recommendation for This Project

**Primary**: **Render** — Your `render.yaml` is already configured! Just push to GitHub and connect.

**Backup Database**: **Neon** — Free PostgreSQL with no 90-day limit.

**Media Files**: **Cloudinary** — 25GB free, handles resumes/logos perfectly.

**Custom Domain**: **Cloudflare** — Free SSL, CDN, DDoS protection.

---

## 📝 Deployment Checklist

- [ ] Push code to GitHub
- [ ] Choose hosting platform
- [ ] Set up PostgreSQL (Neon/Render/Railway/Fly)
- [ ] Configure environment variables
- [ ] Set up Cloudinary for media files
- [ ] Run `python manage.py migrate`
- [ ] Run `python manage.py collectstatic`
- [ ] Create superuser
- [ ] Test all user flows (Student/Company/Admin)
- [ ] Configure custom domain (optional)
- [ ] Set up monitoring (UptimeRobot + Sentry)
- [ ] Document deployment for team

---

## 🆘 Troubleshooting

| Issue | Solution |
|-------|----------|
| `DisallowedHost` | Add domain to `ALLOWED_HOSTS` env var |
| Static files 404 | Run `collectstatic`, check `STATIC_ROOT`, WhiteNoise middleware order |
| Database connection failed | Verify `DATABASE_URL`, check firewall/IP allowlist |
| Media files not loading | Configure Cloudinary or persistent volume |
| `SECRET_KEY` error | Generate new: `openssl rand -base64 32` |
| Migration errors | Check `DATABASE_URL` points to empty DB, run `migrate --plan` |

---

## 📚 Additional Resources

- [Django Deployment Checklist](https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/)
- [Render Django Docs](https://render.com/docs/deploy-django)
- [Railway Django Guide](https://docs.railway.app/guides/django)
- [Fly.io Django Guide](https://fly.io/docs/django/)
- [WhiteNoise Docs](http://whitenoise.evans.io/en/stable/django.html)

---

**Happy Deploying! 🎉** 

Your Placement Management System is production-ready. The `render.yaml` makes Render the fastest path to a live URL.