# La Polla - Django Migration

Django-based betting platform migrated from PHP. This is a complete rewrite of the "La Polla" horse racing and sports betting system.

## 🎯 Project Overview

This Django application is a **complete migration** of the PHP betting platform with:

- **NEW** Django tables (prefixed with `core_`)
- **SAFE** data migration from legacy PHP tables
- **CUSTOM** admin interface (NOT Django's built-in admin)
- **PRESERVED** all business logic and features
- **IMPROVED** security, code organization, and maintainability

### Legacy PHP Tables → New Django Tables

| Legacy Table      | New Django Table          | Status      |
|-------------------|---------------------------|-------------|
| `user`            | `core_user`               | ✅ Migrated |
| `pollas`          | `core_polla`              | ✅ Migrated |
| `eventos`         | `core_evento`             | ✅ Migrated |
| `hipodromo`       | `core_racetrack`          | ✅ Migrated |
| `ligas`           | `core_league`             | ✅ Migrated |
| `equipos`         | `core_team`               | ✅ Migrated |
| `ev_partidos`     | `core_match`              | ✅ Migrated |
| `bets_pollas`     | `core_betpolla`           | ✅ Migrated |
| `bets_eventos`    | `core_betevento`          | ✅ Migrated |
| `bets_ev_partidos`| `core_betmatch`           | ✅ Migrated |
| `ctaCash`         | `core_accounttransaction` | ✅ Migrated |
| `ev_ctaCash`      | `core_eventtransaction`   | ✅ Migrated |

**IMPORTANT:** Legacy tables remain **UNTOUCHED** for safety.

---

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.8 or higher
- MySQL server running
- Virtual environment (recommended)

### 2. Installation

```bash
# Navigate to Django directory
cd django

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your settings
nano .env
```

**IMPORTANT:** Update these in `.env`:
- `DB_PASSWORD`: Your MySQL password
- `SENDGRID_API_KEY`: Your SendGrid API key
- `SECRET_KEY`: Generate a new Django secret key

Generate a secret key:
```bash
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

### 4. Database Setup

```bash
# Create Django tables (legacy tables UNTOUCHED)
python manage.py makemigrations
python manage.py migrate
```

**At this point:**
- ✅ New Django tables created (`core_user`, `core_polla`, etc.)
- ✅ Legacy tables intact (`user`, `pollas`, etc.)
- ✅ Both coexist in the same database

### 5. Data Migration

```bash
# DRY RUN FIRST (recommended)
python manage.py migrate_legacy_data --dry-run

# If dry run looks good, run actual migration
python manage.py migrate_legacy_data
```

**This will:**
1. Copy ALL data from legacy tables to new Django tables
2. Preserve IDs (so relationships remain intact)
3. Verify data integrity
4. Report any issues

**SAFE:** Legacy tables are **NEVER modified**.

### 6. Create Admin User

```bash
# Create your admin account
python manage.py createsuperuser

# Then mark yourself as admin in Django shell
python manage.py shell
```

In the shell:
```python
from core.models import User
user = User.objects.get(email='your@email.com')
user.is_admin = True
user.is_superadmin = True
user.save()
exit()
```

### 7. Run Development Server

```bash
python manage.py runserver
```

Visit:
- **Public site:** http://127.0.0.1:8000/
- **User area:** http://127.0.0.1:8000/inside/
- **Custom admin:** http://127.0.0.1:8000/adm/
- **Django admin (optional):** http://127.0.0.1:8000/django-admin/

---

## 📁 Project Structure

```
django/
├── bets_project/          # Main project settings
│   ├── settings.py        # Django configuration
│   ├── urls.py            # Main URL routing
│   └── wsgi.py            # Production server config
├── core/                  # Core app (models, business logic)
│   ├── models.py          # NEW Django models
│   ├── models_legacy.py   # Read-only access to PHP tables
│   ├── views.py           # Public views (login, register)
│   ├── forms.py           # Authentication forms
│   └── management/
│       └── commands/
│           └── migrate_legacy_data.py  # Data migration script
├── admin_panel/           # Custom admin interface (NOT Django admin)
│   ├── views.py           # Admin views (manage events, results)
│   ├── forms.py           # Admin forms
│   ├── utils.py           # Prize calculation, payments
│   ├── decorators.py      # @admin_required decorator
│   └── urls.py            # Admin URL routing
├── user_area/             # User interface (betting, account)
│   ├── views.py           # User views (dashboard, betting)
│   ├── forms.py           # Betting forms
│   └── urls.py            # User URL routing
├── templates/             # HTML templates
│   ├── base/
│   ├── core/
│   ├── admin_panel/
│   └── user_area/
├── static/                # CSS, JS, images
│   ├── css/
│   ├── js/
│   └── img/
├── manage.py              # Django management
├── requirements.txt       # Python dependencies
└── README.md              # This file
```

---

## 🔐 Admin Access

### Custom Admin Interface (NOT Django Admin)

This project uses a **custom frontend admin interface**, matching the PHP `/adm/` structure.

**Access:** `/adm/`

**Features:**
- Create/manage pollas (horse races)
- Create/manage eventos (sports events)
- Add matches to events
- Enter results
- Process prize payments
- View user accounts

**Permissions:**
- `User.is_admin = True`: Can access `/adm/`
- `User.is_superadmin = True`: Full access including user management

**Why Custom Admin?**
- Frontend-accessible (not hidden like Django admin)
- Matches PHP workflow exactly
- Customizable UI/UX
- Permission-based (not Django's staff/superuser model)

---

## 💰 Business Logic

### Prize Distribution

**Polla (Horse Racing):**
1. Users select 6 horses (one per race)
2. Points awarded for each correct prediction
3. Top scorers split the prize pool

**Evento (Sports):**
1. Users predict match outcomes
2. Points awarded based on bet type:
   - **Type 1:** Exact scores (3 pts), correct winner (1 pt)
   - **Type 3 (NFL):** Winner selection
   - **Type 5/6 (Soccer):** Winner or tie

**Prize Tiers:**
- **< 50 participants:** 70% / 30% (1st / 2nd)
- **≥ 50 participants:** 60% / 25% / 15% (1st / 2nd / 3rd)

**Commissions:**
- **Pollas:** 10% commission, 10% accumulator, 80% prize pool
- **Eventos:** 15% commission, 85% prize pool

### Email Notifications

SendGrid integration sends emails for:
- User registration
- Bet confirmation
- Prize wins
- Password recovery

---

## 🗄️ Database Migration Details

### Migration Process

The `migrate_legacy_data` command:

1. **Migrates reference data:**
   - Racetracks (hipodromo → core_racetrack)
   - Leagues (ligas → core_league)
   - Teams (equipos → core_team)

2. **Migrates users:**
   - Preserves passwords (already bcrypt hashed)
   - Preserves user IDs

3. **Migrates events:**
   - Pollas (horse races)
   - Eventos (sports events)
   - Matches

4. **Migrates bets:**
   - Polla bets with selections
   - Evento bets with predictions

5. **Migrates transactions:**
   - Account transactions (ctaCash)
   - Event transactions (ev_ctaCash)

6. **Verifies integrity:**
   - Counts records
   - Reports discrepancies

### Rollback Strategy

If something goes wrong:
```bash
# Drop all core_ tables
python manage.py migrate core zero

# Re-run migration
python manage.py migrate
python manage.py migrate_legacy_data
```

Legacy data remains safe!

---

## 🧪 Testing

### Manual Testing

```bash
# 1. Verify data migration
python manage.py shell
```

In shell:
```python
from core.models import User, Polla, Evento
from core.models_legacy import LegacyUser, LegacyPolla, LegacyEvento

# Compare counts
print(f"Users: {User.objects.count()} (New) vs {LegacyUser.objects.count()} (Old)")
print(f"Pollas: {Polla.objects.count()} (New) vs {LegacyPolla.objects.count()} (Old)")
print(f"Eventos: {Evento.objects.count()} (New) vs {LegacyEvento.objects.count()} (Old)")

# Test balance calculation
user = User.objects.first()
print(f"User balance: ${user.get_balance()}")
```

### Verify Email

```bash
python manage.py shell
```

In shell:
```python
from django.core.mail import send_mail
send_mail(
    'Test Email',
    'Django email working!',
    'noreply@elguaire.com',
    ['your@email.com'],
)
```

---

## 🚢 Production Deployment

### 1. Update Settings

In `.env`:
```bash
DEBUG=False
SECRET_KEY=<new-production-key>
ALLOWED_HOSTS=bets.elguaire.com,www.bets.elguaire.com
SECURE_SSL_REDIRECT=True
```

### 2. Collect Static Files

```bash
python manage.py collectstatic
```

### 3. Use Production Server

```bash
# Install gunicorn (already in requirements.txt)
pip install gunicorn

# Run with gunicorn
gunicorn bets_project.wsgi:application --bind 0.0.0.0:8000
```

### 4. Configure Web Server

**Nginx Example:**
```nginx
server {
    listen 80;
    server_name bets.elguaire.com;

    location /static/ {
        alias /path/to/django/staticfiles/;
    }

    location /media/ {
        alias /path/to/django/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 🔧 Common Tasks

### Add New Admin User

```bash
python manage.py shell
```

```python
from core.models import User
user = User.objects.get(email='someone@email.com')
user.is_admin = True
user.save()
```

### Reset User Password

```bash
python manage.py shell
```

```python
from core.models import User
user = User.objects.get(email='someone@email.com')
user.set_password('newpassword')
user.save()
```

### View Logs

```bash
tail -f django.log
```

### Backup Database

```bash
# MySQL dump
mysqldump -u web-user-tennis -p elguaire_lapolla > backup.sql
```

---

## 📊 Key Differences from PHP

| Aspect | PHP | Django |
|--------|-----|--------|
| **Tables** | Direct table names | Prefixed with `core_` |
| **Admin** | Custom PHP pages | Custom Django views |
| **Sessions** | PHP sessions | Django sessions |
| **Forms** | Manual HTML | Django Forms |
| **Email** | SendGrid API | Django email backend |
| **Security** | Manual | Built-in (CSRF, SQL injection protection) |
| **ORM** | Raw SQL | Django ORM |

---

## 🆘 Troubleshooting

### MySQL Connection Error

```bash
# Check MySQL is running
mysql -u web-user-tennis -p

# Verify credentials in .env
cat .env
```

### Import Error

```bash
# Reinstall dependencies
pip install -r requirements.txt
```

### Migration Fails

```bash
# Check which migration failed
python manage.py showmigrations

# Reset if needed
python manage.py migrate core zero
python manage.py migrate
```

### SendGrid Not Working

```bash
# Verify API key
echo $SENDGRID_API_KEY

# Test in shell
python manage.py shell
from django.core.mail import send_mail
```

---

## 📝 TODO / Future Enhancements

- [ ] Create all HTML templates (base templates provided)
- [ ] Add unit tests
- [ ] Implement password recovery emails
- [ ] Add 5y6 system views
- [ ] Create API endpoints (optional)
- [ ] Add bet update functionality
- [ ] Implement advanced statistics
- [ ] Add user profile management
- [ ] Create admin reports/analytics

---

## 👥 Support

For issues or questions:
- Check this README
- Review Django logs: `django.log`
- Check MySQL error log
- Review migration output

---

## 📜 License

Proprietary - ElGuaire.com

---

## ✅ Migration Checklist

Before going live with Django:

- [ ] All data migrated successfully
- [ ] User authentication working
- [ ] Betting workflow tested
- [ ] Prize distribution verified
- [ ] Email notifications working
- [ ] Admin interface functional
- [ ] Balance calculations correct
- [ ] Legacy PHP site backed up
- [ ] Database backed up
- [ ] DNS ready to switch
- [ ] SSL certificate configured
- [ ] Static files served correctly

---

**Last Updated:** October 2024
**Django Version:** 4.2.7
**Python Version:** 3.8+
