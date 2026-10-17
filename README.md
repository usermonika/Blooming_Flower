# Blooming Flower

An online flower shop built with Django. Customers can browse products, keep a wishlist, add items to a cart and pay with Stripe or Khalti. Admins manage the shop from the Django admin.

This file explains how to get the project running. For how the project works (apps, models, URLs, features), see [blooming.md](blooming.md).

## Requirements

- Python 3.12
- Git
- (Optional) MySQL, only if you switch away from the default SQLite database

## 1. Get the code

```bash
git clone <your-repo-url> blooming-flower
cd blooming-flower
```

## 2. Create and activate a virtual environment

Windows (PowerShell):

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

macOS / Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

## 4. Configure payment keys

Settings are read with `os.getenv`, and the project does **not** load `.env` automatically. Set the variables in your shell before starting the server. `.env.example` lists the names.

Windows (PowerShell):

```powershell
$env:KHALTI_PUBLIC_KEY = "..."
$env:KHALTI_SECRET_KEY = "..."
$env:KHALTI_VERIFY_URL = "https://khalti.com/api/v2/payment/verify/"
```

macOS / Linux:

```bash
export KHALTI_PUBLIC_KEY="..."
export KHALTI_SECRET_KEY="..."
export KHALTI_VERIFY_URL="https://khalti.com/api/v2/payment/verify/"
```

- **Khalti:** without these keys the rest of the site still works, and Khalti checkout returns a "Khalti is not configured" message.
- **Stripe:** the test keys are currently written directly in `Blooming_Flower/settings.py` (`STRIPE_TEST_PUBLIC_KEY`, `STRIPE_TEST_SECRET_KEY`). Use your own **test** keys from the Stripe dashboard. Never put live keys in the code.

## 5. Set up the database

The project uses SQLite (`db.sqlite3`) by default.

```bash
python manage.py migrate
python manage.py createsuperuser
```

To use MySQL instead, create a database called `blooming`, then in `Blooming_Flower/settings.py` comment out the SQLite `DATABASES` block and uncomment the MySQL one. `PyMySQL` is already installed and enabled in `Blooming_Flower/__init__.py`.

## 6. Run the server

```bash
python manage.py runserver
```

Then open:

| Page | URL |
|---|---|
| Shop home page | http://127.0.0.1:8000/ |
| Products | http://127.0.0.1:8000/product-list/ |
| Login / Register | http://127.0.0.1:8000/register-login/ |
| Admin panel | http://127.0.0.1:8000/admin/ |

To open the site from another device on your network, run `python manage.py runserver 0.0.0.0:8000` and add your computer's IP address to `ALLOWED_HOSTS` in `settings.py`.

## 7. Add some content

Log in to `/admin/` with your superuser and add, in this order:

1. **Categories** and **Colors**
2. **Products** (each needs a category, price, stock and an image)
3. Optional: **Discount offers**, **Upcoming products**, **Blogs**, **Team members**, **Contact info**

Uploaded images are saved in the `media/` folder.

## Testing payments

Stripe runs in test mode. On the checkout page use these test cards:

| Card number | Result |
|---|---|
| `4242 4242 4242 4242` | Payment succeeds |
| `4000 0000 0000 0002` | Card declined |

Use any future expiry date, any 3-digit CVC and any postcode.

## Common problems

| Problem | Fix |
|---|---|
| `ModuleNotFoundError: No module named 'baton'` or `'pymysql'` | Run `pip install -r requirements.txt` inside the activated `.venv` |
| `DisallowedHost` / "Bad Request (400)" | Add the host you are using to `ALLOWED_HOSTS` in `settings.py` |
| Images don't show | Make sure `DEBUG = True` locally; media files are only served by Django in debug mode |
| Login says "Invalid credentials" | Check the email/username and password. Usernames cannot contain spaces |
| Khalti says "not configured" | Set the `KHALTI_*` variables (step 4) in the same terminal before `runserver` |
