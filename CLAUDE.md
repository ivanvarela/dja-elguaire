# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**La Polla** - Django-based horse racing and sports betting platform migrated from PHP. This is a complete rewrite preserving all business logic while improving security and maintainability.

### Key Architecture Principle: Dual-Table Strategy

This project uses a **safe dual-table approach** where:
- **Legacy PHP tables** remain UNTOUCHED (user, pollas, eventos, etc.)
- **New Django tables** are prefixed with `core_` (core_user, core_polla, core_evento, etc.)
- Both coexist in the same MySQL database (`elguaire_lapolla`)
- Data is safely migrated using `manage.py migrate_legacy_data`

## Common Commands

### Development Environment Setup
```bash
# Activate virtual environment (ALWAYS required before any Django command)
source venv_elg/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment (copy and edit JSON config)
cp bets_project/bets.config.json.example bets_project/bets.config.json
# Edit bets_project/bets.config.json with your settings
```

### Database Operations
```bash
# Create Django tables (creates core_* tables, legacy tables untouched)
python manage.py makemigrations
python manage.py migrate

# Migrate data from legacy PHP tables (dry run first)
python manage.py migrate_legacy_data --dry-run
python manage.py migrate_legacy_data

# Rollback Django tables if needed
python manage.py migrate core zero
python manage.py migrate
```

### Development Server
```bash
# Run development server
python manage.py runserver

# Run on different port
python manage.py runserver 8001
```

### User Management
```bash
# Create superuser
python manage.py createsuperuser

# Grant admin permissions (use Django shell)
python manage.py shell
```

In the shell:
```python
from core.models import User
user = User.objects.get(email='admin@example.com')
user.is_admin = True          # Can access /adm/
user.is_superadmin = True     # Full admin access
user.save()
```

### Testing and Debugging
```bash
# Open Django shell for testing
python manage.py shell

# Check migration status
python manage.py showmigrations

# View logs
tail -f django.log
```

### Production Deployment
```bash
# Collect static files
python manage.py collectstatic

# Run with Gunicorn
gunicorn bets_project.wsgi:application --bind 0.0.0.0:8000
```

## High-Level Architecture

### Three-App Structure

**1. `core/` - Business Logic & Models**
- All Django models (User, Polla, Evento, BetPolla, etc.)
- Read-only legacy models in `models_legacy.py`
- Public views (login, register, logout)
- Custom management command: `migrate_legacy_data.py`
- **Key Insight**: `models.py` creates NEW tables, `models_legacy.py` reads OLD tables

**2. `admin_panel/` - Custom Admin Interface**
- **NOT** Django's built-in admin (we built a custom frontend admin)
- URL: `/adm/` (matches PHP structure)
- Manage pollas, eventos, matches, results
- Calculate winners and distribute prizes
- User management (superadmin only)
- **Permission Control**: Use `@admin_required` and `@superadmin_required` decorators

**3. `user_area/` - User Betting Interface**
- URL: `/inside/` (matches PHP structure)
- Dashboard, betting forms, account balance
- View betting history and results
- **Authentication Required**: All views check user login

### Permission System

**Custom permission model** (not Django's default):
- `User.is_admin = True` → Access to `/adm/` area
- `User.is_superadmin = True` → Full admin access including user management
- `User.is_staff` → Optional, only for Django's built-in admin at `/django-admin/`
- `User.is_superuser` → Optional, only for Django admin

**Important**: Always use `is_admin` and `is_superadmin` for custom admin access control, not Django's `is_staff`.

### Database Table Mapping

| Legacy PHP Table | New Django Table | Model |
|------------------|------------------|-------|
| user | core_user | User |
| pollas | core_polla | Polla |
| eventos | core_evento | Evento |
| hipodromo | core_racetrack | Racetrack |
| ligas | core_league | League |
| equipos | core_team | Team |
| ev_partidos | core_match | Match |
| bets_pollas | core_betpolla | BetPolla |
| bets_eventos | core_betevento | BetEvento |
| bets_ev_partidos | core_betmatch | BetMatch |
| ctaCash | core_accounttransaction | AccountTransaction |
| ev_ctaCash | core_eventtransaction | EventTransaction |

### Business Logic: Prize Distribution

**Polla (Horse Racing):**
- 6 races per polla
- 1 point per correct horse prediction
- Commission: 10% admin, 10% accumulator, 80% prize pool
- Prize tiers:
  - < 50 participants: 70%/30% (1st/2nd)
  - ≥ 50 participants: 60%/25%/15% (1st/2nd/3rd)

**Evento (Sports):**
- Multiple matches per evento
- Three bet types (`tipo_juego`):
  - Type 1: Exact scores (3 pts), correct winner (1 pt)
  - Type 3 (NFL): Winner selection only
  - Type 5/6 (Soccer): Winner or tie
- Commission: 15% admin, 85% prize pool
- Same prize tier structure as pollas

**Implementation**: See `admin_panel/utils.py` for prize calculation logic.

### Email Notifications

Uses **SendGrid** via Django email backend:
- User registration confirmation
- Bet confirmation
- Prize win notifications
- Password recovery

**Configuration**: Set `SENDGRID_API_KEY` in `.env` file.

## Important Development Guidelines

### When Adding New Features

1. **Models**: Always add to `core/models.py`, never modify `models_legacy.py`
2. **Migrations**: Run `makemigrations` after model changes, then `migrate`
3. **Forms**: Use Django Forms in respective app (admin_panel or user_area)
4. **Views**: Follow app structure - admin in `admin_panel/`, user in `user_area/`
5. **Templates**: Place in `templates/{app_name}/` directory

### When Modifying Business Logic

1. **Prize Calculation**: See `admin_panel/utils.py` - `calculate_polla_winners()` and `calculate_evento_winners()`
2. **Balance Calculation**: User model has `get_balance()` method that aggregates both transaction tables
3. **Bet Validation**: Check user balance, duplicate bets, event status before saving
4. **Email Sending**: Use Django's `send_mail()` function, configured for SendGrid

### When Working with Transactions

- Two separate transaction tables: `AccountTransaction` (pollas) and `EventTransaction` (eventos)
- Balance = Sum of non-conciliado transactions from both tables
- Transaction types: Apuesta (bet), Premio (prize), Comision (commission), Pote (pot)
- **Never delete transactions** - mark as `conciliado=True` to reconcile

### URL Structure

- `/` - Public homepage (login/register)
- `/login/`, `/register/`, `/logout/` - Authentication
- `/inside/` - User dashboard (requires login)
- `/inside/polla/<code>/` - Bet on polla
- `/inside/evento/<code>/` - Bet on evento
- `/inside/account/` - Transaction history
- `/adm/` - Custom admin dashboard (requires is_admin)
- `/adm/pollas/`, `/adm/eventos/` - Admin management
- `/django-admin/` - Django's built-in admin (optional)

## Data Migration Notes

### Safe Migration Process

The `migrate_legacy_data` command:
1. Migrates reference data (racetracks, leagues, teams)
2. Migrates users (preserves bcrypt passwords)
3. Migrates events (pollas, eventos, matches)
4. Migrates bets (polla bets, evento bets, predictions)
5. Migrates transactions (account and event)
6. Migrates 5y6 system data
7. Verifies integrity (reports count discrepancies)

**Critical**: Legacy tables are NEVER modified. If migration fails, run `python manage.py migrate core zero` to reset Django tables.

### Testing Data Migration

```python
python manage.py shell

from core.models import User, Polla, Evento
from core.models_legacy import LegacyUser, LegacyPolla, LegacyEvento

# Compare counts
print(f"Users: {User.objects.count()} (New) vs {LegacyUser.objects.count()} (Old)")
print(f"Pollas: {Polla.objects.count()} (New) vs {LegacyPolla.objects.count()} (Old)")

# Test balance calculation
user = User.objects.first()
print(f"Balance: ${user.get_balance()}")
```

## Configuration Files

### `bets_project/bets.config.json` - Main Configuration

**Location:**
- Development: `bets_project/bets.config.json`
- Production: `/etc/bets.config.json`

**Required settings:**
```json
{
  "SECRET_KEY": "your-secret-key-here",
  "SENDGRID_API_KEY": "SG.your-sendgrid-key",
  "DB_HOST": "localhost",
  "DB_NAME": "elguaire_lapolla",
  "DB_USER": "web-user-tennis",
  "DB_PASS": "your-password",
  "DB_PORT": "3306",
  "FROM_EMAIL": "noreply@elguaire.com",
  "SITE_URL": "https://bets.elguaire.com",
  "SITE_NAME": "La Polla - ElGuaire"
}
```

**Generate SECRET_KEY:**
```bash
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

**Important:** The config file is git-ignored for security. Always copy from `.example` file.

### `bets_project/settings.py`
- Custom user model: `AUTH_USER_MODEL = 'core.User'`
- Session timeout: 3600 seconds (1 hour)
- Timezone: America/New_York
- Language: Spanish (es)
- DEBUG mode controlled by file location (local vs /etc/)
- Production logging includes email notifications for 500 errors

## Troubleshooting Common Issues

### "Table 'core_user' doesn't exist"
Run migrations: `python manage.py migrate`

### "Access denied for user 'web-user-tennis'"
Check `.env` file has correct `DB_PASSWORD`

### "ModuleNotFoundError: No module named 'django'"
Activate virtual environment: `source venv_elg/bin/activate`

### "No users found" after migration
Run data migration: `python manage.py migrate_legacy_data`

### Email not sending
Verify `SENDGRID_API_KEY` in `.env` and test in Django shell

## Security Notes

- CSRF protection enabled on all forms
- SQL injection prevented by Django ORM
- XSS protection via template auto-escaping
- Password hashing with Django's secure hashers (bcrypt compatible)
- Session security configurable via settings
- SSL/HTTPS enforced in production (DEBUG=False)

## Future Considerations

- HTML templates need completion (base structure provided in `templates/`)
- Unit tests should be added
- API endpoints could be created using Django REST Framework (already installed)
- 5y6 system views need implementation
- Password recovery email functionality to be added
