# Quick Start Guide - Django Migration

**Fast setup for developers familiar with Django**

## 1. Install (5 minutes)

```bash
cd django
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env`:
- Update `DB_PASSWORD`
- Generate new `SECRET_KEY`

## 2. Create Tables (2 minutes)

```bash
python manage.py makemigrations
python manage.py migrate
```

**Result:** New Django tables created (`core_*`). Legacy tables untouched.

## 3. Migrate Data (3 minutes)

```bash
# Dry run first (recommended)
python manage.py migrate_legacy_data --dry-run

# Actual migration
python manage.py migrate_legacy_data
```

**Result:** All data copied from legacy tables to new Django tables.

## 4. Create Admin User (1 minute)

```bash
python manage.py createsuperuser
```

Then mark as admin:
```bash
python manage.py shell
```

```python
from core.models import User
user = User.objects.get(email='your@email.com')
user.is_admin = True
user.is_superadmin = True
user.save()
exit()
```

## 5. Run Server (1 second)

```bash
python manage.py runserver
```

Visit:
- http://127.0.0.1:8000/ (public)
- http://127.0.0.1:8000/inside/ (user area)
- http://127.0.0.1:8000/adm/ (custom admin)

---

## Architecture Overview

```
PHP System (Legacy)          Django System (New)
├── user                →    core_user
├── pollas              →    core_polla
├── eventos             →    core_evento
├── bets_pollas         →    core_betpolla
├── bets_eventos        →    core_betevento
└── ctaCash             →    core_accounttransaction
```

**Both coexist safely in the same database!**

---

## Key Features

✅ **Custom Admin** at `/adm/` (NOT Django's default admin)
✅ **All data preserved** (legacy tables untouched)
✅ **Same business logic** (prize distribution, commissions)
✅ **Email integration** (SendGrid)
✅ **Permission system** (`is_admin`, `is_superadmin`)

---

## Common Commands

```bash
# View data
python manage.py shell

# Check migration
python manage.py showmigrations

# Create migrations
python manage.py makemigrations

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic

# Run tests
python manage.py test
```

---

## Troubleshooting

**Can't connect to database?**
```bash
mysql -u web-user-tennis -p  # Test connection
```

**Import errors?**
```bash
pip install -r requirements.txt  # Reinstall
```

**Data mismatch?**
```bash
python manage.py migrate_legacy_data --dry-run  # Re-check
```

---

## Next Steps

1. Review `README.md` for full documentation
2. Create HTML templates (base templates provided)
3. Test betting workflow
4. Verify email notifications
5. Test prize distribution
6. Deploy to production

---

**Total Setup Time: ~12 minutes**
