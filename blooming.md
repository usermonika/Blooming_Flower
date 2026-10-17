# Blooming Flower — Project Details

This document explains how the Blooming Flower project is built and how each feature works. To install and run it, see [README.md](README.md).

## Overview

Blooming Flower is a flower e-commerce website built with **Django 5.2**. Visitors can:

- browse and search flowers by category and color
- see new arrivals, sale items, discounts and upcoming products
- add products to a cart and a wishlist (with or without an account)
- register, log in and manage a profile with a picture
- check out and pay with **Stripe** (card) or **Khalti** (Nepali wallet)
- view their order history and order details
- rate products, read blogs, like blogs and leave comments
- subscribe to the newsletter

Shop staff manage everything from the Django admin panel (styled with **django-baton**).

## Technology

| Part | Technology |
|---|---|
| Backend | Django 5.2, Python 3.12 |
| API | Django REST Framework (token + session auth) |
| Database | SQLite by default, MySQL supported via PyMySQL |
| Frontend | Django templates, Bootstrap, jQuery, plain JavaScript (`fetch`) |
| Payments | Stripe (test mode), Khalti |
| Admin | Django admin + django-baton theme |
| Images | Pillow, stored in `media/` |

## Project structure

```
blooming-flower/
├── Blooming_Flower/        # Project settings, root URLs, WSGI/ASGI
├── accounts/               # Custom user model, register/login API, profile page
├── Ecommerce/              # All shop models, admin, product API, cart context processor
├── home/                   # Website pages and views (home, cart, checkout, wishlist, blog…)
├── templates/              # HTML templates
│   ├── base/               # base.html (header, mini cart, quick-view modal, footer)
│   ├── shop/               # cart, checkout, orders, mini cart, theme shop pages
│   └── blog/               # blog list and blog detail
├── static/                 # CSS, JS, images
├── media/                  # Uploaded images (products, profiles, team, blogs)
├── db.sqlite3              # Default database
├── requirements.txt
├── README.md               # How to start the project
└── blooming.md             # This file
```

## Apps

### `accounts`

- **`CustomUser`**: extends Django's `AbstractUser` with `role` (admin/customer), `address`, `profile_image` and `is_verified`. Set as `AUTH_USER_MODEL`.
- **Register API**: `POST /user/api/register/` with `username`, `email`, `password`, `confirm`. It validates the username format, rejects duplicate emails and mismatched passwords, then creates the user, logs them in and returns a token.
- **Login API**: `POST /user/api/login/` with `email` and `password`. The email box also accepts a username. It logs the user in with a Django session and returns a token.
- **Profile**: `/user/api/user-profile/` (login required). Edit name, email, address and profile picture, and see counts of orders, wishlist items and reviews.
- **Password change**: `/user/password_change/`.

The login page (`templates/login.html`) calls these APIs with `fetch`, shows field-level validation, and displays the server's error message when something fails.

### `Ecommerce`

Holds the data models, the admin registration and a small REST API.

- **Product API**: `/api/products/` (DRF router, `ProductViewSet`). Requires authentication by default.
- **Context processor** `Ecommerce.context_processors.cart_count`: adds `cart_item_count` and `cart_total` to every page, so the header cart badge is always correct.

### `home`

All customer-facing pages: home, product list, cart, checkout, wishlist, orders, blog, about and contact.

## Data model

| Model | Purpose | Key fields / relations |
|---|---|---|
| `Category` | Product and blog category | name |
| `Color` | Flower colors | name |
| `Product` | A flower for sale | name, description, price, stock, image, label (new/sale/featured), is_new, is_on_sale, sales_count, → `Category`, ↔ `Color`; `avg_rating` property |
| `Review` | Star rating + comment | → `Product`, → `CustomUser` |
| `DiscountOffer` | Time-limited discount | → `Product`, start_date, end_date |
| `UpcomingProduct` | Product not yet released | one-to-one → `Product`, image, release_date |
| `Cart` | A logged-in user's cart | → `CustomUser`, is_active |
| `CartItem` | One line in a cart | → `Cart`, → `Product`, quantity; `total` property |
| `Wishlist` | Saved product | → `CustomUser`, → `Product` |
| `Order` | A placed order | customer and address fields, amount, payment_status (Pending/Paid/Failed), is_delivered, → `CustomUser` (optional) |
| `Blog` | Blog post | title, content, image, date_posted, shares, → `Category`, ↔ `Tag` |
| `Tag` | Blog tag | name |
| `Like` | Blog like | → `Blog`, ip_address (one like per IP per blog), → `CustomUser` (optional) |
| `Comment` | Blog comment | → `Blog`, name, email, message |
| `TeamMember` | About-page team | name, role, description, image, social links |
| `ContactInfo` | Shop contact details | address, phone, email, social links |
| `Subscribe` | Newsletter email | unique email |

An ER diagram is in `schema.png`.

## How the main features work

### Cart

- **Logged-in users**: stored in the database as a `Cart` (with `is_active=True`) and its `CartItem`s.
- **Guests**: stored in the session as `{product_id: quantity}`.
- `GET /add-to-cart/<id>/` from JavaScript returns `{"cart_item_count": n}`, which updates the header badge without reloading. A normal link click redirects to the cart page instead. `POST` (from the quick-view form, with a `quantity`) redirects to the cart.
- The cart page lets you change quantities and remove lines. A flat **Rs 120 shipping** fee is added.

### Wishlist

- Logged-in users: `Wishlist` rows. Guests: a list of product ids in the session.
- `/add-to-wishlist/<id>/` toggles (adds, or removes if already saved) and returns JSON. The heart icons on product cards call it from the script in `templates/base/base.html`.
- `/wishlist-view/` lists saved items with price, stock, add-to-cart and remove.

### Checkout and payment

1. `/checkout/` shows the cart summary and a billing form.
2. On submit, an `Order` is created with status **Pending**.
3. **Stripe**: Stripe.js turns the card into a token in the browser. The server charges it with `stripe.Charge.create`.
   - Success → order marked **Paid** and the cart is emptied.
   - Card declined → order marked **Failed**, the error is shown, and the **cart is kept** so the customer can try again.
4. **Khalti**: the Khalti widget pays in the browser, then `POST /verify-khalti/` checks the payment with Khalti's API and records a Paid order. If the Khalti keys aren't set, it returns a clear "not configured" message.

### Orders

- `/order-history/`: logged-in users see their own orders. Guests can look up orders by phone + email.
- `/order/<id>/`: order detail with items, subtotal, shipping and total (login required; users can only see their own orders).

### Products and search

- `/product-list/` supports `?category=<id>`, `?color=<id>` and `?search=<text>` (searches name and description).
- `/product/<id>/` opens the home page with that product's quick-view modal.
- `/product/quickview/<id>/` returns the quick-view modal content (used by JavaScript).
- `/product/<id>/rate/` (POST, login required) saves or updates the user's rating and comment.

### Home page

Shows released products (products with a future `UpcomingProduct` date are hidden), new arrivals, featured/sale items, active discount offers, the next upcoming product with a countdown, the latest 3 blogs, and the contact info.

### Blog

- `/blogs/`: paginated list (9 per page), filter with `?category=<id>`.
- `/blog/<id>/`: detail page with comments; posting the comment form saves a `Comment`.
- `/like-blog/<id>/`: toggles a like (one per IP address) and returns `{"liked": true/false, "total_likes": n}`.

### Newsletter

`POST /subscribe/` with an `email` returns a JSON success or error message, shown as a toast (`static/js/toast-message.js`).

## URL reference

| URL | View | What it does |
|---|---|---|
| `/` | `home` | Home page |
| `/product/<id>/` | `home` | Home page with product quick view open |
| `/product/quickview/<id>/` | `product_detail` | Quick-view modal content |
| `/product-list/` | `product_list` | All products, filters and search |
| `/product/<id>/rate/` | `rate_product` | Submit a rating (POST, login) |
| `/add-to-cart/<id>/` | `add_to_cart` | Add to cart (JSON or redirect) |
| `/cart/` | `cart` | Cart page, update quantities |
| `/cart/remove/<id>/` | `remove_from_cart` | Remove a cart line |
| `/update_cart_mini/` | `update_cart_mini` | Mini cart HTML + count (JSON) |
| `/checkout/` | `checkout` | Checkout and Stripe payment |
| `/verify-khalti/` | `verify_khalti_payment` | Verify a Khalti payment |
| `/add-to-wishlist/<id>/` | `add_to_wishlist` | Toggle wishlist (JSON) |
| `/wishlist-view/` | `wishlist_view` | Wishlist page |
| `/wishlist/remove/<id>/` | `remove_from_wishlist` | Remove from wishlist |
| `/order-history/` | `order_history` | Order list / guest lookup |
| `/order/<id>/` | `order_detail` | Order detail (login) |
| `/blogs/` | `blog_list` | Blog list |
| `/blog/<id>/` | `blog_detail` | Blog detail + comments |
| `/like-blog/<id>/` | `like_blog` | Toggle blog like (JSON) |
| `/subscribe/` | `subscribe` | Newsletter signup (POST, JSON) |
| `/about-us/` | `aboutus` | About page with team |
| `/contact-us/` | `contact` | Contact page |
| `/register-login/` | `register_login` | Login and registration page |
| `/logout/` | `logout_view` | Log out and go home |
| `/user/api/register/` | `register_user` | Register API (POST, JSON) |
| `/user/api/login/` | `login_user` | Login API (POST, JSON) |
| `/user/api/user-profile/` | `user_profile` | Profile page (login) |
| `/user/password_change/` | Django | Change password |
| `/api/products/` | `ProductViewSet` | Product REST API (auth) |
| `/admin/` | Django admin | Manage the whole shop |

## Admin panel

Every model above is registered in `/admin/`, so staff can add products, set discounts and upcoming releases, write blogs, manage team members and contact info, see orders and mark them delivered, and manage users. The admin is themed by django-baton (settings under `BATON` in `settings.py`).

## Known limitations and next steps

- **Secrets in code**: the Stripe test keys are hard-coded in `settings.py` and `.env.example`. Move them to environment variables, and roll the keys if this repository was ever shared.
- **Currency**: Stripe charges in `usd`, but prices are in Nepali Rupees, so the amount charged doesn't match the price shown. Switch the currency to `npr`, or convert the amount.
- **`.env` not loaded**: settings use `os.getenv`, but nothing loads the `.env` file. `python-dotenv` would fix this.
- **Duplicate emails**: email is not unique on `CustomUser`. New registrations now reject duplicate emails, but some older accounts share one.
- **Stripe Charges API**: the project uses the older Charges + token flow. Stripe recommends Payment Intents for new work, which also supports 3-D Secure cards.
- **Product page route**: `/product/<id>/` is declared twice in `home/urls.py`, so the `product_detail` name always resolves to the home view, and `product_detail.html` does not exist.
- **Theme pages**: `/shop/<name>/` renders the original template's static demo pages (not linked from the menu).
- **Production**: `DEBUG = True` and the `SECRET_KEY` is in the code. Turn debug off, move the secret key into an environment variable, and serve static and media files properly before deploying.
