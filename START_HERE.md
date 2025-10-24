# 🚀 START HERE - Django Migration Setup Guide

**Complete step-by-step instructions to migrate your PHP betting platform to Django**

⏱️ **Total Time:** ~20 minutes
🎯 **Difficulty:** Easy - just follow the steps
⚠️ **Safety:** Your PHP data remains 100% untouched

---

## 📋 **Pre-Flight Checklist**

Before starting, make sure you have:

- [ ] Python 3.8 or higher installed (`python3 --version`)
- [ ] MySQL server running with your existing database
- [ ] Database credentials: `elguaire_lapolla` / `web-user-tennis` / `**Tennis_2022++`
- [ ] SendGrid API key (already in the code)
- [ ] Terminal/command line access
- [ ] 20 minutes of uninterrupted time

---

## 🎬 **STEP 1: Open Terminal and Navigate to Project**

```bash
# Open your terminal and navigate to the Django folder
cd /Users/ivanvarela/PhpstormProjects/bets/django

# Verify you're in the right place (should show manage.py, requirements.txt, etc.)
ls -la

# You should see:
# manage.py
# requirements.txt
# README.md
# bets_project/
# core/
# etc.
```

✅ **Checkpoint:** You should see the Django project files listed.

---

## 🎬 **STEP 2: Create Python Virtual Environment**

```bash
# Create a virtual environment named 'venv'
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Your terminal prompt should now show (venv) at the beginning
# Example: (venv) ivanvarela@MacBook bets %
```

✅ **Checkpoint:** Your prompt should show `(venv)` at the start.

**Note:** If you close the terminal, you'll need to activate again with:
```bash
source venv/bin/activate
```

---

## 🎬 **STEP 3: Install Python Dependencies**

```bash
# Install all required packages (Django, MySQL, SendGrid, etc.)
pip install -r requirements.txt

# This will take 2-3 minutes
# You'll see lots of "Successfully installed..." messages
```

✅ **Checkpoint:** Should end with "Successfully installed..." messages, no errors.

**If you see errors about mysqlclient:**

**On macOS:**
```bash
brew install mysql-client pkg-config
export PKG_CONFIG_PATH="/usr/local/opt/mysql-client/lib/pkgconfig"
pip install mysqlclient
```

**On Ubuntu/Linux:**
```bash
sudo apt-get install python3-dev default-libmysqlclient-dev build-essential
pip install mysqlclient
```

---

## 🎬 **STEP 4: Configure Environment Variables**

```bash
# Copy the environment template
cp .env.example .env

# Generate a Django secret key
python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'

# Copy the output (it's a long random string)
```

**Now edit the .env file:**

```bash
# Open .env in your editor
nano .env

# OR use VS Code:
code .env

# OR use vim:
vim .env
```

**Update these lines in .env:**

1. **SECRET_KEY** - Paste the key you just generated:
   ```
   SECRET_KEY=django-insecure-abc123xyz789...
   ```

2. **Verify database settings** (should already be correct):
   ```
   DB_NAME=elguaire_lapolla
   DB_USER=web-user-tennis
   DB_PASSWORD=**Tennis_2022++
   DB_HOST=localhost
   DB_PORT=3306
   ```

3. **Verify SendGrid key** (should already be set):
   ```
   SENDGRID_API_KEY=your-sendgrid-api-key-here
   ```

**Save and close the file:**
- In nano: Press `Ctrl+X`, then `Y`, then `Enter`
- In vim: Press `Esc`, type `:wq`, press `Enter`
- In VS Code: Just save normally

✅ **Checkpoint:** `.env` file exists with your SECRET_KEY filled in.

**Verify it worked:**
```bash
cat .env | grep SECRET_KEY
# Should show your secret key
```

---

## 🎬 **STEP 5: Test Database Connection**

```bash
# Test that you can connect to MySQL
mysql -u web-user-tennis -p
# Enter password: **Tennis_2022++

# In MySQL prompt:
USE elguaire_lapolla;
SHOW TABLES;

# You should see your existing PHP tables:
# user
# pollas
# eventos
# etc.

# Exit MySQL
exit;
```

✅ **Checkpoint:** You can connect to MySQL and see your existing tables.

---

## 🎬 **STEP 6: Create Django Database Tables**

**This creates NEW tables (core_*) WITHOUT touching your PHP tables.**

```bash
# Create migration files
python manage.py makemigrations

# Expected output:
# Migrations for 'core':
#   core/migrations/0001_initial.py
#     - Create model User
#     - Create model Racetrack
#     - Create model League
#     ... etc.
```

```bash
# Apply migrations (creates the tables)
python manage.py migrate

# Expected output:
# Running migrations:
#   Applying contenttypes.0001_initial... OK
#   Applying core.0001_initial... OK
#   ... etc.
```

✅ **Checkpoint:** Should see "OK" for all migrations, no errors.

---

## 🎬 **STEP 7: Verify Django Tables Were Created**

```bash
# Connect to MySQL again
mysql -u web-user-tennis -p
# Enter password: **Tennis_2022++
```

```sql
-- In MySQL prompt:
USE elguaire_lapolla;

-- Show all tables starting with 'core_'
SHOW TABLES LIKE 'core_%';

-- You should see NEW tables:
-- core_user
-- core_polla
-- core_evento
-- core_racetrack
-- core_league
-- core_team
-- core_match
-- core_betpolla
-- core_betevento
-- core_betmatch
-- core_accounttransaction
-- core_eventtransaction
-- etc.

-- Show your OLD tables (unchanged)
SHOW TABLES LIKE 'user';
SHOW TABLES LIKE 'pollas';
SHOW TABLES LIKE 'eventos';

-- These should still exist!

-- Exit MySQL
exit;
```

✅ **Checkpoint:** You should see BOTH old tables AND new `core_*` tables.

**Important:** Your old tables (user, pollas, eventos) are still there, UNCHANGED! ✅

---

## 🎬 **STEP 8: Migrate Your Data (DRY RUN FIRST)**

**First, let's do a DRY RUN to see what will happen without actually changing anything:**

```bash
# Dry run - shows what WOULD happen
python manage.py migrate_legacy_data --dry-run

# You'll see output like:
# Starting data migration from legacy tables...
#
# Migrating racetracks...
#   ✓ Migrated 5 racetracks
# Migrating leagues...
#   ✓ Migrated 3 leagues
# Migrating teams...
#   ✓ Migrated 45 teams
# Migrating users...
#   ✓ Migrated 150 users
# Migrating pollas...
#   ✓ Migrated 200 pollas
# Migrating eventos...
#   ✓ Migrated 50 eventos
# ... etc.
#
# Verifying migration...
#   Users: 150 (New) vs 150 (Old)
#   Pollas: 200 (New) vs 200 (Old)
#   Eventos: 50 (New) vs 50 (Old)
#   ✓ Verification complete
#
# DRY RUN - Rolling back...
```

**Review the output carefully:**
- ✅ Counts should match (New vs Old)
- ✅ Should say "✓ Migrated X records" for each type
- ✅ Should end with "DRY RUN - Rolling back..."

✅ **Checkpoint:** Dry run completes with no errors, counts look reasonable.

---

## 🎬 **STEP 9: Migrate Your Data (ACTUAL MIGRATION)**

**If the dry run looked good, now run the real migration:**

```bash
# Actual migration - copies data to new tables
python manage.py migrate_legacy_data

# Same output as dry run, but this time it SAVES the data
# Should end with:
# ======================================================================
# MIGRATION COMPLETED SUCCESSFULLY!
# ======================================================================
# All data has been migrated to new Django tables.
# Legacy tables remain UNTOUCHED.
```

⏱️ **This may take 1-3 minutes depending on how much data you have.**

✅ **Checkpoint:** Should end with "MIGRATION COMPLETED SUCCESSFULLY!"

---

## 🎬 **STEP 10: Verify Data Migration**

```bash
# Open Django shell
python manage.py shell
```

**In the Python shell, run these commands:**

```python
from core.models import User, Polla, Evento, BetPolla, BetEvento
from core.models_legacy import LegacyUser, LegacyPolla, LegacyEvento

# Compare record counts
print("="*60)
print("DATA MIGRATION VERIFICATION")
print("="*60)
print(f"Users:        {User.objects.count():4d} (New) vs {LegacyUser.objects.count():4d} (Old)")
print(f"Pollas:       {Polla.objects.count():4d} (New) vs {LegacyPolla.objects.count():4d} (Old)")
print(f"Eventos:      {Evento.objects.count():4d} (New) vs {LegacyEvento.objects.count():4d} (Old)")
print(f"Polla Bets:   {BetPolla.objects.count():4d} (New)")
print(f"Evento Bets:  {BetEvento.objects.count():4d} (New)")
print("="*60)

# Test a user's balance
user = User.objects.first()
if user:
    print(f"\nSample User:")
    print(f"  Alias: {user.alias}")
    print(f"  Email: {user.email}")
    print(f"  Balance: ${user.get_balance()}")
    print(f"  Is Admin: {user.is_admin}")
else:
    print("\nNo users found!")

# Exit the shell
exit()
```

✅ **Checkpoint:** Counts should match exactly between New and Old.

**Expected output example:**
```
============================================================
DATA MIGRATION VERIFICATION
============================================================
Users:         150 (New) vs  150 (Old)
Pollas:        200 (New) vs  200 (Old)
Eventos:        50 (New) vs   50 (Old)
Polla Bets:    350 (New)
Evento Bets:   120 (New)
============================================================

Sample User:
  Alias: JuanPerez
  Email: juan@example.com
  Balance: $125.50
  Is Admin: False
```

---

## 🎬 **STEP 11: Create Your Admin User**

```bash
# Create a superuser account
python manage.py createsuperuser

# You'll be prompted:
# Email: (enter your email)
# Alias: (enter your name/alias)
# Password: (enter a strong password)
# Password (again): (repeat the password)

# Example:
# Email: ivan.varela@gmail.com
# Alias: Ivan Varela
# Password: ••••••••
# Password (again): ••••••••
# Superuser created successfully.
```

**Now mark yourself as admin:**

```bash
# Open Django shell
python manage.py shell
```

```python
from core.models import User

# Get your newly created user (use YOUR email)
user = User.objects.get(email='ivan.varela@gmail.com')

# Grant admin permissions
user.is_admin = True
user.is_superadmin = True
user.save()

# Verify
print(f"✓ {user.alias} is now an admin!")
print(f"  is_admin: {user.is_admin}")
print(f"  is_superadmin: {user.is_superadmin}")

# Exit
exit()
```

✅ **Checkpoint:** Should see confirmation that you're now an admin.

---

## 🎬 **STEP 12: Run the Development Server**

```bash
# Start Django development server
python manage.py runserver

# Expected output:
# Watching for file changes with StatReloader
# Performing system checks...
#
# System check identified no issues (0 silenced).
# October 23, 2024 - 10:00:00
# Django version 4.2.7, using settings 'bets_project.settings'
# Starting development server at http://127.0.0.1:8000/
# Quit the server with CONTROL-C.
```

✅ **Checkpoint:** Server starts without errors.

**Keep this terminal window open! The server must run for you to access the site.**

---

## 🎬 **STEP 13: Test in Your Browser**

**Open your web browser and test these URLs:**

### 1. Homepage
- **URL:** http://127.0.0.1:8000/
- **Expected:** Login/Register page
- **Test:** Should load without errors

### 2. Login
- **URL:** http://127.0.0.1:8000/login/
- **Test:** Login with your admin credentials (from Step 11)
- **Expected:** Redirects to dashboard

### 3. User Dashboard
- **URL:** http://127.0.0.1:8000/inside/
- **Expected:**
  - Shows your balance
  - Shows active pollas/eventos
  - Shows navbar with your name

### 4. Account Detail
- **URL:** http://127.0.0.1:8000/inside/account/
- **Expected:** Shows transaction history

### 5. Custom Admin Panel
- **URL:** http://127.0.0.1:8000/adm/
- **Expected:**
  - Admin dashboard
  - Links to manage pollas/eventos
  - User management (superadmin only)

### 6. Django Admin (Optional)
- **URL:** http://127.0.0.1:8000/django-admin/
- **Expected:** Django's built-in admin interface
- **Note:** This is optional - we built a custom admin at /adm/

✅ **Checkpoint:** All pages load without errors, you can login and see data.

---

## 🎬 **STEP 14: Test Core Functionality**

### Test 1: View Balance
1. Go to http://127.0.0.1:8000/inside/
2. Check your balance displays correctly
3. Go to http://127.0.0.1:8000/inside/account/
4. Verify transactions are listed

### Test 2: View Events
1. Check if you see any active pollas
2. Check if you see any active eventos
3. Click on one to see details

### Test 3: Admin Functions (if you're admin)
1. Go to http://127.0.0.1:8000/adm/
2. Click "Administrar Pollas"
3. Verify you see existing pollas
4. Click "Administrar Eventos"
5. Verify you see existing eventos

✅ **Checkpoint:** Everything displays correctly, no errors.

---

## 🎉 **SUCCESS! You're Done!**

Your Django application is now running with all your data migrated!

### What You've Accomplished:

✅ Created a Django project structure
✅ Installed all dependencies
✅ Created new database tables (core_*)
✅ Migrated ALL data from PHP to Django
✅ Created an admin user
✅ Started the development server
✅ Tested the application

### What's Safe:

✅ **Your PHP tables:** UNTOUCHED and safe
✅ **Your PHP application:** Still works normally
✅ **Your data:** Copied (not moved) to Django

---

## 📊 **What You Have Now**

```
Your MySQL Database (elguaire_lapolla)
├── PHP Tables (ORIGINAL - UNCHANGED)
│   ├── user
│   ├── pollas
│   ├── eventos
│   └── ... (all your data is still here)
│
└── Django Tables (NEW - POPULATED)
    ├── core_user
    ├── core_polla
    ├── core_evento
    └── ... (all your data COPIED here too)
```

**Both systems can run simultaneously!**

---

## 🔄 **Stopping and Restarting**

### To Stop the Server:
```bash
# In the terminal where server is running:
# Press CONTROL+C
```

### To Restart Later:
```bash
# Navigate to project
cd /Users/ivanvarela/PhpstormProjects/bets/django

# Activate virtual environment
source venv/bin/activate

# Start server
python manage.py runserver
```

---

## 🐛 **Troubleshooting**

### Problem: "ModuleNotFoundError: No module named 'django'"

**Solution:**
```bash
# Make sure virtual environment is activated
source venv/bin/activate

# You should see (venv) in your prompt
# If not, you forgot to activate it
```

### Problem: "Access denied for user 'web-user-tennis'"

**Solution:**
```bash
# Verify .env has correct password
cat .env | grep DB_PASSWORD

# Test MySQL connection
mysql -u web-user-tennis -p
# If this fails, your password is wrong
```

### Problem: "Table 'core_user' doesn't exist"

**Solution:**
```bash
# Run migrations
python manage.py migrate
```

### Problem: "No users found" in verification

**Solution:**
```bash
# Run the data migration
python manage.py migrate_legacy_data
```

### Problem: Port 8000 already in use

**Solution:**
```bash
# Use a different port
python manage.py runserver 8001

# Then visit http://127.0.0.1:8001/
```

### Problem: Page shows "Page not found (404)"

**Solution:**
- Check the URL is correct
- Make sure server is running
- Check terminal for errors

### Problem: Migration shows count mismatch

**Solution:**
This is usually OK! Some tables might not exist in your PHP database yet (like 5y6 tables). As long as main tables (user, pollas, eventos) match, you're good.

---

## 📝 **Commands Cheat Sheet**

```bash
# Navigate to project
cd /Users/ivanvarela/PhpstormProjects/bets/django

# Activate virtual environment
source venv/bin/activate

# Start server
python manage.py runserver

# Stop server
CONTROL+C

# Open Django shell
python manage.py shell

# Run migrations
python manage.py migrate

# Create new migrations (after model changes)
python manage.py makemigrations

# Migrate data from PHP
python manage.py migrate_legacy_data

# Create superuser
python manage.py createsuperuser
```

---

## 🎯 **Next Steps (After Testing)**

### Option 1: Keep Testing (Recommended)
- Test all betting workflows
- Test prize calculations
- Test email notifications
- Compare with PHP to ensure parity

### Option 2: Develop More
- Create custom HTML templates
- Add more features
- Customize the design
- Add unit tests

### Option 3: Prepare for Production
- Review `README.md` for deployment guide
- Configure production settings
- Set up Gunicorn + Nginx
- Get SSL certificate

---

## ⚠️ **Important Reminders**

1. **Your PHP data is SAFE** - Legacy tables are never modified
2. **You can start over** - Delete core_* tables and re-migrate anytime
3. **Both systems can coexist** - PHP and Django can run together
4. **Always activate venv** - Before running Django commands
5. **Keep this file** - For reference when you restart

---

## 📞 **Need Help?**

If you get stuck:

1. **Check the error message** in the terminal
2. **Look at the logs:** `tail -f django.log`
3. **Review this file** - Troubleshooting section
4. **Check README.md** - More detailed documentation
5. **Verify each step** - Make sure you didn't skip anything

---

## ✅ **Final Checklist**

Before considering this complete, verify:

- [ ] Virtual environment created and activated
- [ ] All dependencies installed
- [ ] .env file configured
- [ ] Django tables created (core_*)
- [ ] Data migrated successfully
- [ ] Record counts match (Old vs New)
- [ ] Admin user created
- [ ] Server runs without errors
- [ ] Can login to website
- [ ] Can access dashboard
- [ ] Can access admin panel
- [ ] Balance displays correctly

---

**Congratulations! Your Django migration is complete!** 🎉

**Created:** October 2024
**Django Version:** 4.2.7
**Python Version:** 3.8+
**Estimated Time:** 20 minutes
**Difficulty:** ⭐⭐ (Easy)
